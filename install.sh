python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
(crontab -l && echo "0 0 * * * cd $(pwd); ./venv/bin/python main.py") | crontab -
