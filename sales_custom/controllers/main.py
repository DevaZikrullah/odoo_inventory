import requests
from urllib.parse import parse_qs

from odoo import http
from odoo.http import request, _logger
from requests.auth import HTTPBasicAuth
import logging
import threading


class SaleOrderController(http.Controller):

    @http.route('/api/accurate', type='json', auth='public')
    def get_data_accurate(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        customer = self.get_customer(access_token, session)
        # product = self.get_product_accurate(access_token, session)
        # so = self.get_so_accurate(access_token, session)

        return {
            'status': 200,
            'data': customer
        }

    def get_customer(self, access_token, session):
        url = 'https://zeus.accurate.id/accurate/api/customer/list.do?fields=id,name,customerNo&sp.pageSize=100'

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
                        'customer name': item['name'],
                        'customer id': item['id'],
                        'customer no': item['customerNo'],
                    }

                    existing_record = request.env['res.partner'].search(
                        [('customer_accurate_no', '=', item['customerNo'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_user_templates(data_to_create)
                            data_to_create = []
                    else:
                        existing_record.write({
                            'customer_rank': 1
                        })

                if data_to_create:
                    self.create_user_templates(data_to_create)

            return {
                'data': 'ok'
            }

    def create_user_templates(self, data_to_create):
        product_template_obj = request.env['res.partner']
        records_to_create = []

        for item in data_to_create:
            record_vals = {
                'name': item['customer name'],
                'customer_accurate_id': item['customer id'],
                'customer_accurate_no': item['customer no']
            }
            records_to_create.append(record_vals)

        product_template_obj.sudo().create(records_to_create)

    def get_access_token(self):
        url = 'https://account.accurate.id/oauth/authorize'
        client_id = '8de2a1e6-4b1c-4ca2-8898-f0bd18ed0447'
        redirect_uri = 'http://localhost:8069/web/assets/aol-oauth-callback'
        scope = 'purchase_invoice_view+item_view+sales_invoice_view+customer_view+vendor_view'
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
        url = "https://zeus.accurate.id/accurate/api/item/list.do?fields=id,name,no,quantity,vendorUnit&sp.pageSize=100"

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
                        'Item Stock': item['quantity'],
                    }

                    existing_record = request.env['product.template'].search(
                        [('item_accurate_number', '=', item['no'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_product_templates(data_to_create)
                            data_to_create = []
                    else:
                        if item['vendorUnit'] != None:
                            self.update_avail_stock(item['no'], item['quantity'], item['vendorUnit']['name'])

            if data_to_create:
                self.create_product_templates(data_to_create)

            return {
                'item': data['d'],
            }
        else:
            return {
                'error': f"Error: {response.status_code}"
            }

    # @http.route('/api/accurate', type='json', auth='public')
    def detail_po_store(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = f'https://zeus.accurate.id/accurate/api/purchase-invoice/detail.do?id=10958'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)

        data = response.json()['d']
        # print(data)
        # # print('aowkaow')
        # exit()

        day, month, year = data['shipDate'].split('/')
        ymd_date = f"{year}-{month}-{day}"
        formatted_data = {
            'name': data['billNumber'],
            'date_planned': ymd_date,
            'item_accurate_id': data['id'],
            'vendor_accurate': data['vendor']['name'],
            'partner_id': 1,
            'state': 'purchase'
            # 'subTotal': data['subTotal']
        }

        print(formatted_data)

        purchase_create = request.env['purchase.order'].sudo().create(formatted_data)

        for value in data['detailItem']:
            product_id = request.env['product.template'].search([('item_accurate_id', '=', value['itemId'])])
            # print(product_id)
            item = {
                'product_id': int(product_id),
                'name': value['detailName'],
                'product_qty': value['quantity'],
                'price_unit': value['unitPrice'],
                'order_id': purchase_create.id,
                'price_tax': 0
            }
            request.env['purchase.order.line'].sudo().create(item)

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

    def update_avail_stock(self, item_no, qty, uom):
        if uom is not None:
            uom_type = request.env['uom.uom'].search([('name', '=', uom)])
            id_product = request.env['product.template'].search([('item_accurate_number', '=', item_no)])
            id_product.write({
                'type': 'product',
                'uom_id': int(uom_type)
            })
            request.env['stock.quant'].sudo().create({
                'product_id': int(id_product),
                'location_id': 8,
                'quantity': qty
            })

    def open_db_accurate(self, access_token):
        url = 'https://account.accurate.id/api/open-db.do?id=683745'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)

        return response.json()

    def get_po_accurate(self, access_token, session):

        product = request.env['product.template']
        purchase = request.env['purchase.order']
        purchase_order = request.env['purchase.order.line']
        url = "https://zeus.accurate.id/accurate/api/purchase-invoice/list.do?sp.pageSize=100"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            for page in range(1, 1 + 1):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    id_item = item['id']  # Store 'item['id']' in the list
                    records_purchase_create = []

                    url = f'https://zeus.accurate.id/accurate/api/purchase-invoice/detail.do?id={id_item}'

                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'X-Session-ID': session
                    }

                    response = requests.get(url, headers=headers)
                    data = response.json()['d']
                    day, month, year = data['shipDate'].split('/')
                    ymd_date = f"{year}-{month}-{day}"
                    formatted_data = {
                        'name': data['billNumber'],
                        'date_planned': ymd_date,
                        'item_accurate_id': data['id'],
                        'vendor_accurate': data['vendor']['name'],
                        'partner_id': 1,
                        'state': 'purchase'
                        # 'subTotal': data['subTotal']
                    }

                    records_purchase_create.append(formatted_data)

                    existing_record = product.search(
                        [('item_accurate_id', '=', data['id'])])

                    if not existing_record:
                        # Create records using the env ORM context
                        purchase_create = purchase.sudo().create(formatted_data)
                        for value in data['detailItem']:
                            product_id = product.search(
                                [('item_accurate_id', '=', value['itemId'])])
                            item = {
                                'product_id': product_id.id,
                                'name': value['detailName'],
                                'product_qty': value['quantity'],
                                'price_unit': value['unitPrice'],
                                'order_id': purchase_create.id,
                                'price_tax': 0
                            }
                            purchase_order.sudo().create(item)

                        _logger.info("Background function finished")

    def get_so_accurate(self, access_token, session):

        product = request.env['product.template']
        purchase = request.env['sale.order']
        purchase_order = request.env['sale.order.line']
        url = "https://zeus.accurate.id/accurate/api/sales-invoice/list.do?sp.pageSize=100"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)
        id_list = []
        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            for page in range(1, 1 + 1):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    id_item = item['id']  # Store 'item['id']' in the list
                    records_purchase_create = []

                    url = f'https://zeus.accurate.id/accurate/api/sales-invoice/detail.do?id={id_item}'

                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'X-Session-ID': session
                    }

                    response = requests.get(url, headers=headers)
                    data = response.json()['d']
                    day, month, year = data['shipDate'].split('/')
                    ymd_date = f"{year}-{month}-{day}"
                    formatted_data = {
                        'name': data['number'],
                        'date_order': ymd_date,
                        'item_accurate_id': data['id'],
                        'customer': data['customer']['name'],
                        'partner_id': 1,
                        # 'state': 'purchase'
                        # 'subTotal': data['subTotal']
                    }

                    records_purchase_create.append(formatted_data)

                    existing_record = product.search(
                        [('item_accurate_id', '=', data['id'])])

                    if not existing_record:
                        # Create records using the env ORM context
                        purchase_create = purchase.sudo().create(formatted_data)

                        for value in data['detailItem']:
                            product_id = product.search(
                                [('item_accurate_id', '=', value['itemId'])])
                            item = {
                                'product_id': product_id.id,
                                'name': value['detailName'],
                                'product_uom_qty': value['quantity'],
                                'price_unit': value['unitPrice'],
                                'order_id': purchase_create.id,
                                'price_tax': 0
                            }
                            purchase_order.sudo().create(item)

                        _logger.info("Background function finished")
            return {
                'data': data
            }


class PurchaseOrderImporter:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def __init__(self, access_token, session):
        self.access_token = access_token
        self.session = session
        self.product_model = request.env['product.template']
        self.purchase_model = request.env['purchase.order']
        self.purchase_order_model = request.env['purchase.order.line']
        self.base_url = "https://zeus.accurate.id/accurate/api"
        self.logger = logging.getLogger(__name__)

    #
    # def detail_po_store(self):
    #
    #     url = f'https://zeus.accurate.id/accurate/api/purchase-invoice/detail.do?id=10958'
    #
    #     headers = {
    #         'Authorization': f'Bearer {self.access_token}',
    #         'X-Session-ID': self.session
    #     }
    #
    #     response = requests.get(url, headers=headers)
    #
    #     data = response.json()['d']
    #     # print(data)
    #     # # print('aowkaow')
    #     # exit()
    #
    #     day, month, year = data['shipDate'].split('/')
    #     ymd_date = f"{year}-{month}-{day}"
    #     formatted_data = {
    #         'name': data['billNumber'],
    #         'date_planned': ymd_date,
    #         'item_accurate_id': data['id'],
    #         'vendor_accurate': data['vendor']['name'],
    #         'partner_id': 1,
    #         'state': 'purchase'
    #         # 'subTotal': data['subTotal']
    #     }
    #
    #     existing_record = request.env['purchase.order'].search(
    #         [('item_accurate_id', '=', data['id'])])
    #     if not existing_record:
    #         purchase_create = request.env['purchase.order'].sudo().create(formatted_data)
    #
    #         for value in data['detailItem']:
    #             product_id = request.env['product.template'].search([('item_accurate_id', '=', value['itemId'])])
    #             # print(product_id)
    #             item = {
    #                 'product_id': int(product_id),
    #                 'name': value['detailName'],
    #                 'product_qty': value['quantity'],
    #                 'price_unit': value['unitPrice'],
    #                 'order_id': purchase_create.id,
    #                 'price_tax': 0
    #             }
    #             request.env['purchase.order.line'].sudo().create(item)
