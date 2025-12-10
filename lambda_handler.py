from mangum import Mangum
from insurance_parser_api import app

lambda_handler = Mangum(app)