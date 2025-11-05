# UrSaviour EC2 Deployment Guide

## 🚀 EC2 + MySQL 简単デプロイメント

このガイドでは、AWS EC2インスタンス上でUrSaviourアプリケーションを動かす方法を説明します。

### 📋 前提条件

- AWS EC2インスタンス (Ubuntu 20.04+ または Amazon Linux 2)
- SSH アクセス権限
- セキュリティグループでポート80、8000が開いている

### 🎯 クイックデプロイメント

EC2インスタンスで以下を実行：

```bash
# 1. プロジェクトをクローン
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# 2. 完全自動デプロイメント（推奨）
./deploy-ec2-full.sh
```

これで完了！`http://your-ec2-public-ip` でアクセスできます。

### 🔧 手動セットアップ（詳細制御が必要な場合）

#### ステップ1: MySQLセットアップ
```bash
./setup-ec2-mysql.sh
```

#### ステップ2: アプリケーション起動
```bash
./start-ec2-app.sh
```

### 📁 ファイル構成

- `setup-ec2-mysql.sh` - MySQL自動インストール・設定
- `start-ec2-app.sh` - アプリケーション起動
- `deploy-ec2-full.sh` - 完全自動デプロイメント（nginx含む）
- `nginx-ec2.conf` - nginx設定ファイル

### 🔍 トラブルシューティング

#### MySQLの問題
```bash
# MySQL状態確認
sudo systemctl status mysql

# MySQL再起動
sudo systemctl restart mysql

# MySQL ログ確認
sudo tail -f /var/log/mysql/error.log
```

#### アプリケーションの問題
```bash
# バックエンドサービス状態確認
sudo systemctl status ursaviour-backend

# バックエンドログ確認
sudo journalctl -u ursaviour-backend -f

# 手動でバックエンド起動（デバッグ用）
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### nginxの問題
```bash
# nginx状態確認
sudo systemctl status nginx

# nginx設定テスト
sudo nginx -t

# nginxログ確認
sudo tail -f /var/log/nginx/error.log
```

### 🛡️ セキュリティ設定

#### EC2セキュリティグループ
以下のポートを開いてください：
- **HTTP**: Port 80 (Source: 0.0.0.0/0)
- **HTTPS**: Port 443 (Source: 0.0.0.0/0) ※SSL証明書設定後
- **SSH**: Port 22 (Source: Your IP only)

#### データベースセキュリティ
```bash
# MySQL root パスワード変更
sudo mysql_secure_installation

# ファイアウォール設定（Ubuntu）
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### 🌐 ドメイン設定（オプション）

1. Route 53でドメインを設定
2. nginx設定ファイルの`server_name`を変更
3. SSL証明書を設定（Let's Encrypt推奨）

```bash
# SSL証明書設定（Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 📊 モニタリング

#### ログ監視
```bash
# リアルタイムログ監視
sudo journalctl -u ursaviour-backend -f &
sudo tail -f /var/log/nginx/access.log &
```

#### ヘルスチェック
```bash
# バックエンドヘルスチェック
curl http://localhost:8000/docs

# フロントエンドヘルスチェック
curl http://localhost/
```

### 🔄 アップデート手順

```bash
# 1. 新しいコードを取得
git pull origin main

# 2. バックエンド再起動
sudo systemctl restart ursaviour-backend

# 3. フロントエンド更新
sudo cp -r frontend /var/www/ursaviour/

# 4. nginx再読み込み
sudo systemctl reload nginx
```

### 💡 パフォーマンス最適化

#### MySQL調整
```sql
-- /etc/mysql/mysql.conf.d/mysqld.cnf に追加
[mysqld]
innodb_buffer_pool_size = 128M
max_connections = 100
query_cache_size = 64M
```

#### nginx調整
```nginx
# worker プロセス数を CPU コア数に合わせる
worker_processes auto;
worker_connections 1024;
```

### 📞 サポート

問題が発生した場合：
1. ログを確認
2. [GitHub Issues](https://github.com/JustinCoKA/UrSaviour-Project/issues) で報告
3. サービス状態を確認

---

## 🆚 Docker vs EC2 直接インストール

| 項目 | Docker | EC2直接 |
|------|---------|---------|
| **セットアップ** | やや複雑 | シンプル |
| **パフォーマンス** | 若干のオーバーヘッド | ネイティブ |
| **保守性** | 良い | 普通 |
| **スケーラビリティ** | 良い | 普通 |
| **トラブルシューティング** | やや困難 | 簡単 |

**推奨**: 開発・テスト環境では EC2直接インストール、本番環境では要件に応じて選択。