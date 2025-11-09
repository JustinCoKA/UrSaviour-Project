-- ================================================================
-- Sample Discount Data for Product P0001 (Mineral Water)
-- Test discount connection between localhost and AWS RDS
-- ================================================================

-- 1. Check current product data
SELECT 
    p.productId,
    p.productName,
    p.categoryName,
    p.basePrice,
    p.description
FROM products p
WHERE p.productId = 'P0001';

-- ================================================================
-- 2. Add Store Information (if not exists)
-- ================================================================

-- Coles Store
INSERT IGNORE INTO stores (storeId, storeName, location, contactInfo)
VALUES 
    (1, 'Coles', 'Sydney CBD', '{"phone": "1300-635-035", "website": "https://www.coles.com.au"}'),
    (2, 'Woolworths', 'Sydney CBD', '{"phone": "1300-767-969", "website": "https://www.woolworths.com.au"}'),
    (3, 'ALDI', 'Sydney CBD', '{"phone": "1300-425-34", "website": "https://www.aldi.com.au"}');

-- ================================================================
-- 3. Add Base Prices for Each Store
-- ================================================================

INSERT INTO store_base_prices (storeId, productId, basePrice, effectiveDate)
VALUES 
    -- Coles: Mineral Water regular price $7.50
    (1, 'P0001', 7.50, '2025-01-01'),
    
    -- Woolworths: Mineral Water regular price $7.99
    (2, 'P0001', 7.99, '2025-01-01'),
    
    -- ALDI: Mineral Water regular price $6.50
    (3, 'P0001', 6.50, '2025-01-01')
ON DUPLICATE KEY UPDATE
    basePrice = VALUES(basePrice),
    effectiveDate = VALUES(effectiveDate);

-- ================================================================
-- 4. Add Discount Offerings (Special Prices)
-- ================================================================

-- Current week discounts for Mineral Water
INSERT INTO storeOfferings (
    storeId, 
    productId, 
    price, 
    offerDetails, 
    batch_id, 
    loaded_at
)
VALUES 
    -- Coles: 30% OFF - $7.50 -> $5.25
    (1, 'P0001', 5.25, '30% OFF - Buy 2 Get 1 Free', 'WEEK45_2025', NOW()),
    
    -- Woolworths: 25% OFF - $7.99 -> $5.99
    (2, 'P0001', 5.99, '25% OFF - Special Weekend Deal', 'WEEK45_2025', NOW()),
    
    -- ALDI: 20% OFF - $6.50 -> $5.20
    (3, 'P0001', 5.20, '20% OFF - Member Exclusive', 'WEEK45_2025', NOW())
ON DUPLICATE KEY UPDATE
    price = VALUES(price),
    offerDetails = VALUES(offerDetails),
    loaded_at = NOW();

-- ================================================================
-- 5. Verify the discount data
-- ================================================================

SELECT 
    s.storeName,
    p.productName,
    p.basePrice as originalPrice,
    sbp.basePrice as storeBasePrice,
    so.price as discountPrice,
    ROUND(((sbp.basePrice - so.price) / sbp.basePrice * 100), 2) as discountPercent,
    so.offerDetails,
    so.loaded_at
FROM storeOfferings so
JOIN stores s ON so.storeId = s.storeId
JOIN products p ON so.productId = p.productId
LEFT JOIN store_base_prices sbp ON so.storeId = sbp.storeId AND so.productId = sbp.productId
WHERE so.productId = 'P0001'
ORDER BY so.price ASC;

-- ================================================================
-- 6. Check all products with discounts
-- ================================================================

SELECT 
    p.productId,
    p.productName,
    p.categoryName,
    COUNT(DISTINCT so.storeId) as storesWithDiscount,
    MIN(so.price) as lowestPrice,
    MAX(so.price) as highestPrice,
    AVG(so.price) as avgPrice
FROM products p
LEFT JOIN storeOfferings so ON p.productId = so.productId
WHERE p.productId = 'P0001'
GROUP BY p.productId, p.productName, p.categoryName;

-- ================================================================
-- 7. API Response Preview (What frontend will see)
-- ================================================================

SELECT JSON_OBJECT(
    'productId', p.productId,
    'productName', p.productName,
    'categoryName', p.categoryName,
    'description', p.description,
    'basePrice', p.basePrice,
    'defaultImageUrl', p.defaultImageUrl,
    'stores', (
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'storeId', s.storeId,
                'storeName', s.storeName,
                'price', so.price,
                'originalPrice', COALESCE(sbp.basePrice, p.basePrice),
                'discount', CONCAT(
                    ROUND(((COALESCE(sbp.basePrice, p.basePrice) - so.price) / COALESCE(sbp.basePrice, p.basePrice) * 100), 0),
                    '% OFF'
                ),
                'offerDetails', so.offerDetails,
                'savings', ROUND(COALESCE(sbp.basePrice, p.basePrice) - so.price, 2)
            )
        )
        FROM storeOfferings so
        JOIN stores s ON so.storeId = s.storeId
        LEFT JOIN store_base_prices sbp ON so.storeId = sbp.storeId AND so.productId = sbp.productId
        WHERE so.productId = p.productId
    )
) as apiResponse
FROM products p
WHERE p.productId = 'P0001';

-- ================================================================
-- BONUS: Add more sample discounts for testing
-- ================================================================

-- Add discounts for Lettuce (P0002)
INSERT INTO storeOfferings (storeId, productId, price, offerDetails, batch_id, loaded_at)
VALUES 
    (1, 'P0002', 0.79, 'Fresh Pick - 20% OFF', 'WEEK45_2025', NOW()),
    (2, 'P0002', 0.69, 'Super Fresh - 30% OFF', 'WEEK45_2025', NOW()),
    (3, 'P0002', 0.75, 'Daily Special', 'WEEK45_2025', NOW())
ON DUPLICATE KEY UPDATE
    price = VALUES(price),
    offerDetails = VALUES(offerDetails),
    loaded_at = NOW();

-- Add discounts for Custard (P0003)
INSERT INTO storeOfferings (storeId, productId, price, offerDetails, batch_id, loaded_at)
VALUES 
    (1, 'P0003', 0.75, 'Half Price Sale', 'WEEK45_2025', NOW()),
    (2, 'P0003', 0.79, '20% OFF', 'WEEK45_2025', NOW())
ON DUPLICATE KEY UPDATE
    price = VALUES(price),
    offerDetails = VALUES(offerDetails),
    loaded_at = NOW();

-- ================================================================
-- 8. Final Check - Products with Best Discounts
-- ================================================================

SELECT 
    p.productId,
    p.productName,
    s.storeName as bestStore,
    so.price as discountedPrice,
    COALESCE(sbp.basePrice, p.basePrice) as originalPrice,
    CONCAT(
        ROUND(((COALESCE(sbp.basePrice, p.basePrice) - so.price) / COALESCE(sbp.basePrice, p.basePrice) * 100), 0),
        '%'
    ) as discount,
    so.offerDetails
FROM products p
JOIN storeOfferings so ON p.productId = so.productId
JOIN stores s ON so.storeId = s.storeId
LEFT JOIN store_base_prices sbp ON so.storeId = sbp.storeId AND so.productId = sbp.productId
WHERE p.productId IN ('P0001', 'P0002', 'P0003')
ORDER BY 
    ((COALESCE(sbp.basePrice, p.basePrice) - so.price) / COALESCE(sbp.basePrice, p.basePrice)) DESC,
    p.productId ASC;
