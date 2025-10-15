set -e

echo "🟡 Coletando arquivos estáticos: *.js & *.css ..."
echo no | python src/manage.py collectstatic --noinput > /dev/null 2>&1
echo "✅ Coletando arquivos estáticos com sucesso!"

echo "🟡 Migrando o banco de dados..."
python src/manage.py makemigrations utils authentication armoreddjango
echo "✅ Migrando o banco de dados com sucesso!"
python src/manage.py migrate --noinput

python src/manage.py shell -c "from authentication.models import Profile; \
                           Profile.objects.filter(username='admin').exists() or \
                           Profile.objects.create_superuser(username='admin',
                           email='admin@example.com', password='$ADMIN_PASSWORD', profileType=1,
                           first_name='Admin', last_name='User')"

cd /app/src

if [ "$PRODUCTION" = "True" ]; then
    echo "🟡 Iniciando em modo PRODUÇÃO..."
    gunicorn --config gunicorn_config.py armoreddjango.wsgi:application
else
    echo "🟡 Iniciando em modo DESENVOLVIMENTO..."
    python manage.py runserver 0.0.0.0:8003
fi