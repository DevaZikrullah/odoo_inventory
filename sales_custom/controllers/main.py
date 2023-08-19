import requests
from urllib.parse import parse_qs
from odoo import http
from odoo.http import request
from requests.auth import HTTPBasicAuth


class SaleOrderController(http.Controller):

    @http.route('/api/accurate', type='json', auth='public')
    def get_data_accurate(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        product = self.get_product_accurate(access_token, session)

        return {
            'status': 200,
            'data': product
        }

    def get_access_token(self):
        url = 'https://account.accurate.id/oauth/authorize'
        client_id = '8de2a1e6-4b1c-4ca2-8898-f0bd18ed0447'
        redirect_uri = 'http://localhost:8069/web/assets/aol-oauth-callback'
        scope = 'purchase_invoice_view+item_view+sales_invoice_view'
        username = 'noviamardiyanti85@gmail.com'
        password = '@Herman998'
        response = requests.get(url,
                                auth=HTTPBasicAuth(username, password),
                                params={
                                    'client_id': client_id,
                                    'response_type': 'token',
                                    'redirect_uri': redirect_uri,
                                    'scope': scope
                                })

        parsed_url = parse_qs(response.url)
        token_type = parsed_url.get('token_type', [None])[0]
        expires_in = parsed_url.get('expires_in', [None])[0]
        access_token = ""
        url = response.url
        url_parts = url.split("/")
        last_part = url_parts[-1].split("&")
        result_array = url_parts[:-1] + last_part
        for index, value in enumerate(result_array):
            if index == 5:
                access_token = value.split("#")[1].replace("access_token=", "")

        response_data = {
            'access_token': access_token,
            'token_type': token_type,
            'expires_in': expires_in
        }

        return response_data

    def get_product_accurate(self, access_token, session):
        url = "https://zeus.accurate.id/accurate/api/item/list.do?fields=id,name,no&sp.pageSize=100"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']

            batch_size = 50
            data_to_create = []

            for page in range(1, page_count + 1):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    extracted_item = {
                        'Item ID': item['id'],
                        'Item Name': item['name'],
                        'Item Number': item['no'],
                    }

                    existing_record = request.env['product.template'].search([('item_accurate_number', '=', item['no'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_product_templates(data_to_create)
                            data_to_create = []

            if data_to_create:
                self.create_product_templates(data_to_create)

            return {
                'item': data_to_create,
            }
        else:
            return {
                'error': f"Error: {response.status_code}"
            }

    def create_product_templates(self, data_to_create):
        product_template_obj = request.env['product.template']
        records_to_create = []

        for item in data_to_create:
            record_vals = {
                'name': item['Item Name'],
                'item_accurate_id': item['Item ID'],
                'item_accurate_number': item['Item Number']
            }
            records_to_create.append(record_vals)

        product_template_obj.sudo().create(records_to_create)

    def open_db_accurate(self, access_token):
        url = 'https://account.accurate.id/api/open-db.do?id=683745'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)

        return response.json()
