echo "Creating of python venv"
python3 -m venv venv
source venv/bin/activate

echo "Installing libraries"
pip install -r requirements.txt

echo "Adding task to cron" 
(crontab -l && echo "0 0 * * * cd $(pwd); ./venv/bin/python main.py") | crontab -

echo "Введите токен для авторизации пользователя"
read vk_token
touch .env 
(echo "TOKEN=${vk_token}") >> .env
echo "Done"
