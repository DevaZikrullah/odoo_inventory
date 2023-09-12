import requests
from urllib.parse import parse_qs

import odoo
from odoo import http
from odoo.http import request, _logger
from requests.auth import HTTPBasicAuth
import logging
import threading


class SaleOrderController(http.Controller):

    def get_data_accurate(self, date_from, date_to):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        # cust = self.get_customer(access_token,session)
        # product = self.get_product_accurate(access_token, session)
        self.get_so_accurate(access_token, session, date_from, date_to)
        print(access_token)
        print(session)
        return {
            'status': 200,
            'data': 'sucess'
        }
        #
        # return {
        #     'status': 200,
        #     'token': access_token,
        #     'session': session
        # }

    def get_customer(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
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

    def get_vendor(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = 'https://zeus.accurate.id/accurate/api/vendor/list.do?fields=id,name,vendorNo&sp.pageSize=100'

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

            for page in range(1, page_count):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    extracted_item = {
                        'vendor name': item['name'],
                        'vendor id': item['id'],
                        'vendor no': item['vendorNo'],
                    }

                    existing_record = request.env['res.partner'].search(
                        [('vendor_accurate_no', '=', item['vendorNo'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_vendor_templates(data_to_create)
                            data_to_create = []

                if data_to_create:
                    self.create_vendor_templates(data_to_create)

            return {
                'data': 'ok'
            }

    def create_vendor_templates(self, data_to_create):
        product_template_obj = request.env['res.partner']
        records_to_create = []

        for item in data_to_create:
            record_vals = {
                'name': item['vendor name'],
                'vendor_accurate_id': item['vendor id'],
                'vendor_accurate_no': item['vendor no'],
                'supplier_rank': 1
            }
            records_to_create.append(record_vals)

        product_template_obj.sudo().create(records_to_create)

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
        scope = 'purchase_order_view+item_view+sales_order_view+customer_view+vendor_view'
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

    @http.route('/api/accurate-product', type='http', auth="public")
    def get_product_accurate(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
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
                        'Item Uom': item['vendorUnit']['name'] if 'vendorUnit' in item and item['vendorUnit'] else 'PCS'
                    }

                    existing_record = request.env['product.template'].search(
                        [('item_accurate_number', '=', item['no'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_product_templates(data_to_create)
                            data_to_create = []
                    else:
                        if item['vendorUnit'] is not None:
                            self.update_avail_stock(item['no'], item['quantity'])

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
        url = f'https://zeus.accurate.id/accurate/api/purchase-order/detail.do?id=10958'

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
            if item['Item Uom'] is not None:
                uom_type = request.env['uom.uom'].search([('name', '=', item['Item Uom'])], limit=1)

                if not uom_type:
                    uom_category = request.env['uom.category'].create({
                        'name': item['Item Uom']
                    })

                    uom_type.create({
                        'name': item['Item Uom'],
                        'category_id': uom_category.id
                    })

                record_vals = {
                    'name': item['Item Name'],
                    'item_accurate_id': item['Item ID'],
                    'item_accurate_number': item['Item Number'],
                    'uom_id': int(uom_type),
                    'uom_po_id': int(uom_type),
                    'detailed_type': 'product'
                }
                records_to_create.append(record_vals)

        product_template_obj.sudo().create(records_to_create)

    def update_avail_stock(self, item_no, qty):
        product_template = request.env['product.template'].search([('item_accurate_number', '=', item_no)])

        if product_template:
            product_id = product_template.product_variant_id.id
            quant_record = request.env['stock.quant'].search([('product_id', '=', product_id)])

            if not quant_record:
                request.env['stock.quant'].sudo().create({
                    'product_id': product_id,
                    'location_id': 8,
                    'quantity': qty
                })
            else:
                quant_record.write({
                    'quantity': qty
                })

    def open_db_accurate(self, access_token):
        url = 'https://account.accurate.id/api/open-db.do?id=683745'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)

        return response.json()

    def get_po_accurate(self, from_date, to_date):
        product = request.env['product.template']
        purchase = request.env['purchase.order']
        purchase_order = request.env['purchase.order.line']
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = f'https://zeus.accurate.id/accurate/api/purchase-order/list.do?sp.pageSize=100&filter.transDate.op' \
              f'=BETWEEN&filter.transDate.val={from_date}&filter.transDate.val={to_date}'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            for page in range(1, page_count):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    id_item = item['id']  # Store 'item['id']' in the list
                    records_purchase_create = []
                    url = f'https://zeus.accurate.id/accurate/api/purchase-order/detail.do?id={id_item}'
                    print(url)

                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'X-Session-ID': session
                    }

                    response = requests.get(url, headers=headers)
                    data = response.json()['d']
                    day, month, year = data['shipDate'].split('/')
                    ymd_date = f"{year}-{month}-{day}"
                    vendor_id = request.env['res.partner'].search(
                        [('vendor_accurate_id', '=', data['vendorId'])], limit=1)
                    result = 1 if int(vendor_id) == 0 else int(vendor_id)
                    formatted_data = {
                        'name': data['number'],
                        'date_planned': ymd_date,
                        'item_accurate_id': data['id'],
                        'vendor_accurate': data['vendor']['name'],
                        'partner_id': result,
                        'state': 'purchase'
                        # 'subTotal': data['subTotal']
                    }

                    records_purchase_create.append(formatted_data)

                    existing_record = purchase.search(
                        [('item_accurate_id', '=', str(data['id']))])
                    if not existing_record:
                        # print(type(data['id']))

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

    def get_so_accurate(self, access_token, session, from_date, to_date):
        product = request.env['product.template']
        sale = request.env['sale.order']
        sale_order = request.env['sale.order.line']
        url = f'https://zeus.accurate.id/accurate/api/sales-order/list.do?sp.pageSize=100&filter.transDate.op' \
              f'=BETWEEN&filter.transDate.val={from_date}&filter.transDate.val={to_date}'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }
        records_so_create = []

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            for page in range(1, page_count):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                print(data_url)
                for item in items_url:
                    id_item = item['id']  # Store 'item['id']' in the list

                    url_item = f'https://zeus.accurate.id/accurate/api/sales-order/detail.do?id={id_item}'

                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'X-Session-ID': session
                    }

                    response = requests.get(url_item, headers=headers)
                    if response.status_code == 200:
                        data = response.json()['d']
                        day, month, year = data['shipDate'].split('/')
                        ymd_date = f"{year}-{month}-{day}"
                        customer_id = request.env['res.partner'].search(
                            [('customer_accurate_id', '=', data['customerId'])], limit=1)

                        result = 'unknown' if int(customer_id) == 0 else int(customer_id)
                        data_cust = result
                        print(result)
                        if result == 'unknown':
                            data_cust = request.env['res.partner'].search(
                                [('name', '=', result)], limit=1)

                        status = ''
                        if data['statusName'] == 'Menunggu diproses':
                            status = 'Belum Difakturkan'
                        elif data['statusName'] == 'Terproses':
                            status = 'Sudah Difakturkan'
                        print(data_cust)
                        formatted_data = {
                            'name': data['number'],
                            'date_order': ymd_date,
                            'item_accurate_id': data['id'],
                            'customer': data['customer']['name'],
                            'partner_id': int(data_cust),
                            'accurate_address': data['toAddress'],
                            'has_been_invoiced': status,
                            'state': 'sale'
                        }

                        records_so_create.append(formatted_data)

                        existing_record = sale.search(
                            [('item_accurate_id', '=', data['id'])])

                        if not existing_record:
                            sale_order_data = sale.sudo().create(formatted_data)

                            for value in data['detailItem']:
                                product_id = product.search(
                                    [('item_accurate_id', '=', value['itemId'])])
                                item = {
                                    'product_id': product_id.id,
                                    'name': value['detailName'],
                                    'product_uom_qty': value['quantity'],
                                    'price_unit': value['unitPrice'],
                                    'order_id': sale_order_data.id,
                                    'price_tax': 0
                                }
                                sale_order.sudo().create(item)

                            _logger.info("Background function finished")
        return {
            'data': records_so_create
        }

    # def accurate_so_sync(self, id_so):
    #     access_token = self.get_access_token()['access_token']
    #     session = self.open_db_accurate(access_token)['session']
    #     url_item = f'https://zeus.accurate.id/accurate/api/sales-invoice/detail.do?id={id_so}'
    #
    #     headers = {
    #         'Authorization': f'Bearer {access_token}',
    #         'X-Session-ID': session
    #     }
    #
    #     response = requests.get(url_item, headers=headers)
    #     if response.status_code == 200:
    #         data = response.json()['d']
    #         for value in data['detailItem']:
    #             item = {
    #                 'product_id': product_id.id,
    #                 'name': value['detailName'],
    #                 'product_uom_qty': value['quantity'],
    #                 'price_unit': value['unitPrice'],
    #                 'order_id': sale_order_data.id,
    #                 'price_tax': 0
    #             }
