# backend/run.py

import os
os.environ['INFORMER_PROJECT_PATH'] = 'D:\\formal\Informer2020-main'

from app import create_app
# 在 backend/run.py 或任意路由中添加
app = create_app()


print("Informer路径:", os.getenv("INFORMER_PROJECT_PATH"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # 允许外部访问
