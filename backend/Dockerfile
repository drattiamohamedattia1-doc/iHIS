FROM python:3.11-slim

WORKDIR /app

# تثبيت أدوات النظام اللازمة
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي كود المشروع
COPY . .

# إنشاء مجلد المرفوعات
RUN mkdir -p uploads

# نسخ سكربت الدخول (entrypoint.sh) وجعله قابلاً للتنفيذ
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# تجهيز المنفذ
EXPOSE 5000

# استخدام entrypoint.sh كنقطة دخول (يقوم بتنفيذ الترحيل والبيانات الأولية ثم Gunicorn)
ENTRYPOINT ["/entrypoint.sh"]