#!/bin/bash

# AWS RDS Setup Guide for Team
echo "🚀 UrSaviour Team Database Setup (AWS RDS)"

echo "
📋 AWS RDS MySQL インスタンス作成手順

1. AWSコンソールにログイン
   - RDS サービスに移動
   - 「データベースの作成」をクリック

2. 基本設定
   - エンジンタイプ: MySQL
   - バージョン: 8.0 (最新)
   - テンプレート: 本番稼働用 または 開発/テスト用

3. インスタンス設定
   - DBインスタンス識別子: ursaviour-db
   - マスターユーザー名: admin
   - マスターパスワード: [安全なパスワードを設定]

4. インスタンス設定
   - DBインスタンスクラス: db.t3.micro (無料利用枠)
   - ストレージ: gp2, 20GB

5. 接続設定
   - VPC: デフォルトVPC
   - パブリックアクセス: はい (開発用)
   - セキュリティグループ: 新規作成

6. データベース設定
   - 初期データベース名: ursaviour
   - バックアップ: 自動バックアップを有効

7. セキュリティグループ設定
   - タイプ: MySQL/Aurora
   - ポート: 3306
   - ソース: 0.0.0.0/0 (開発用) または EC2のセキュリティグループ

📝 作成後に取得する情報:
   - エンドポイント: ursaviour-db.xxxxxxxxx.ap-southeast-2.rds.amazonaws.com
   - ポート: 3306
   - ユーザー名: admin
   - パスワード: [設定したパスワード]
"

echo "
🔧 チームメンバー用の接続設定:

.env ファイルに以下を設定:
DATABASE_URL=mysql+pymysql://admin:PASSWORD@ENDPOINT:3306/ursaviour

例:
DATABASE_URL=mysql+pymysql://admin:securepassword123@ursaviour-db.xxxxxxxxx.ap-southeast-2.rds.amazonaws.com:3306/ursaviour
"