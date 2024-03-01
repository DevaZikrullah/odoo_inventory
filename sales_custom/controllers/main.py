import requests
from urllib.parse import parse_qs
import json

import odoo
from odoo import http
from odoo.http import request, _logger
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError
import datetime
import threading


class SaleOrderController(http.Controller):

    def get_data_accurate(self, date_from, date_to):
        access_token = self.get_access_token()['access_token']
        print(access_token)
        session = self.open_db_accurate(access_token)['session']
        # cust = self.get_customer(access_token,session)
        # product = self.get_product_accurate(access_token, session)
        self.get_so_accurate(access_token, session, date_from, date_to)
        return {
            'status': 200,
            'data': 'sucess'
        }

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

                    # else:
                    #     existing_record.write({
                    #         'customer_rank': 1
                    #     })

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
                'customer_accurate_no': item['customer no'],
                'customer_rank' : 1
            }
            records_to_create.append(record_vals)

        product_template_obj.sudo().create(records_to_create)

    def get_access_token(self):
        newest_token = request.env['token.accurate'].search([], order='create_date desc', limit=1)
        data = {
            'access_token' : newest_token.name
        }
        return data

    def create_item_adjustment_records(self):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        item_adjustment_accurate_in = request.env['stock.picking'].create({
            'name': 'AAI/' + formatted_datetime.replace(' ', '/'),
            'origin': 'AAI/' + formatted_datetime.replace(' ', '/'),
            'picking_type_id': 7,
            'location_id': 14,
            'location_dest_id': 8,
            'state': 'assigned'
        })

        item_adjustment_accurate_out = request.env['stock.picking'].create({
            'name': 'AAO/' + formatted_datetime.replace(' ', '/'),
            'origin': 'AAO/' + formatted_datetime.replace(' ', '/'),
            'picking_type_id': 8,
            'location_id': 8,
            'location_dest_id': 14,
            'state': 'assigned'
        })

        return item_adjustment_accurate_in, item_adjustment_accurate_out

    def get_product_accurate_qty(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = "https://zeus.accurate.id/accurate/api/item/list.do?fields=id,name,no,quantity,vendorUnit&sp.pageSize=100"

        item_adjustment_accurate_in, item_adjustment_accurate_out = self.create_item_adjustment_records()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            current_datetime = datetime.datetime.now()

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

                    if existing_record:
                        if item['vendorUnit'] is not None:
                            self.update_avail_stock(item['id'], item['quantity'], item_adjustment_accurate_in,
                                                    item_adjustment_accurate_out)

            if item_adjustment_accurate_out and item_adjustment_accurate_out.move_lines:
                item_adjustment_accurate_out.write({
                    'state': 'assigned'
                })
            elif item_adjustment_accurate_in and item_adjustment_accurate_in.move_lines:
                item_adjustment_accurate_in.write({
                    'state': 'assigned'
                })
            elif item_adjustment_accurate_in and not item_adjustment_accurate_in.move_lines:
                item_adjustment_accurate_in.unlink()
            elif item_adjustment_accurate_out and not item_adjustment_accurate_out.move_lines:
                item_adjustment_accurate_out.unlink()

            return {
                'item': data['d'],
            }
        else:
            return {
                'error': f"Error: {response.status_code}"
            }

    def get_product_accurate(self):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = "https://zeus.accurate.id/accurate/api/item/list.do?fields=id,name,no,quantity,vendorUnit&sp.pageSize=100"

        # Create item_adjustment_in and item_adjustment_out records
        item_adjustment_accurate_in, item_adjustment_accurate_out = self.create_item_adjustment_records()

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
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            for page in range(1, page_count + 1):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']

                for item in items_url:
                    extracted_item = {
                        'Item ID': item['id'],
                        'Item Name': item['name'],
                        'Item Number': item['no'],
                        # 'Item Stock': item['quantity'],
                        'Item Uom': item['vendorUnit']['name'] if 'vendorUnit' in item and item['vendorUnit'] else 'PCS'
                    }

                    existing_record = request.env['product.template'].search(
                        [('item_accurate_number', '=', item['no'])])

                    if not existing_record:
                        data_to_create.append(extracted_item)

                        if len(data_to_create) >= batch_size:
                            self.create_product_templates(data_to_create)
                            data_to_create = []
                    elif existing_record:
                        existing_record.write({
                            'name': item['name'],
                            'item_accurate_number': item['no']
                        })


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

    def update_avail_stock(self, item_id, qty, item_adjustment_in_id, item_adjustment_out_id):
        product_template = request.env['product.template'].search([('item_accurate_id', '=', item_id)],limit=1)
        stock_move = request.env['stock.move.line']

        if product_template:
            quant_record = request.env['stock.quant'].search([
                ('product_id', '=', int(product_template))
            ], limit=1, order='id desc')

            if qty < quant_record.quantity:
                # Decrement the available stock quantity
                stock_move.create({
                    'product_id': int(product_template),
                    'picking_id': item_adjustment_out_id.id,
                    'product_uom_id': product_template.uom_id.id,
                    'location_id': item_adjustment_out_id.location_id.id,
                    'location_dest_id': item_adjustment_out_id.location_dest_id.id,
                    'qty_done': quant_record.quantity - qty,
                })
                print(stock_move)
                print('out')
            elif qty > quant_record.quantity:
                stock_move.create({
                    'product_id': int(product_template),
                    'picking_id': item_adjustment_in_id.id,
                    'product_uom_id': product_template.uom_id.id,
                    'product_uom_qty': quant_record.quantity - qty,
                    'location_id': item_adjustment_in_id.location_id.id,
                    'location_dest_id': item_adjustment_in_id.location_dest_id.id,
                    'qty_done': qty - quant_record.quantity,
                })
                print(stock_move)
                print('in')
            elif qty == quant_record.quantity:
                pass

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
        product_template_obj = request.env['product.product']
        vendor = request.env['res.partner']
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
                    id_item = item['id']
                    records_purchase_create = []
                    url = f'https://zeus.accurate.id/accurate/api/purchase-order/detail.do?id={id_item}'

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
                    records_to_create_vendor = []
                    created_vendor = None

                    if not vendor_id:
                        created_vendor = vendor.sudo().create({
                            'name': data['vendor']['name'],
                            'vendor_accurate_id': data['vendor']['id'],
                            'vendor_accurate_no': data['vendor']['vendorNo'],
                            'supplier_rank': 1
                        })

                        records_to_create_vendor.append(created_vendor)

                    formatted_data = {
                        'name': data['number'],
                        'date_planned': ymd_date,
                        'item_accurate_id': data['id'],
                        'vendor_accurate': data['vendor']['name'],
                        'partner_id': created_vendor.id if created_vendor else vendor_id.id,
                        'state': 'purchase'
                    }

                    records_purchase_create.append(formatted_data)

                    existing_record = purchase.search(
                        [('item_accurate_id', '=', str(data['id']))])

                    create_po_order_lines = []

                    if not existing_record:
                        purchase_create = purchase.sudo().create(formatted_data)
                        created_product = []

                        for value in data['detailItem']:
                            product_id = product.search(
                                [('item_accurate_id', '=', value['itemId'])],limit=1)

                            if not product_id:
                                if value['item']['unit1']['name'] is not None:
                                    uom_type = request.env['uom.uom'].search(
                                        [('name', '=', value['item']['unit1']['name'])],
                                        limit=1)

                                    if not uom_type:
                                        uom_category = request.env['uom.category'].create({
                                            'name': value['item']['unit1']['name']
                                        })

                                        uom_type.create({
                                            'name': value['item']['unit1']['name'],
                                            'category_id': uom_category.id
                                        })

                                    created_product_vals = {
                                        'name': value['item']['name'],
                                        'item_accurate_id': value['item']['id'],
                                        'item_accurate_number': value['item']['no'],
                                        'uom_id': int(uom_type),
                                        'uom_po_id': int(uom_type),
                                        'detailed_type': 'product',
                                    }

                                    created_product.append(created_product_vals)

                                    created_product_record = product_template_obj.sudo().create(created_product_vals)

                                    item = {
                                        'product_id': created_product_record.id,
                                        'name': value['detailName'],
                                        'product_qty': value['quantity'],
                                        'price_unit': value['unitPrice'],
                                        'order_id': purchase_create.id,
                                        'taxes_id': [(5, 0, 0)]
                                    }

                                    create_po_order_lines.append(item)


                            else:

                                item = {
                                    'product_id': product_id.id,
                                    'name': value['detailName'],
                                    'product_qty': value['quantity'],
                                    'price_unit': value['unitPrice'],
                                    'order_id': purchase_create.id,
                                    'taxes_id': [(5, 0, 0)]
                                }
                                create_po_order_lines.append(item)

                            purchase_order.create(create_po_order_lines)

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
            for page in range(1, page_count + 1):
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
                        if result == 'unknown':
                            data_cust = request.env['res.partner'].search(
                                [('name', '=', result)], limit=1)

                        status = ''
                        if data['statusName'] == 'Menunggu diproses':
                            status = 'Belum Difakturkan'

                            salesman_so = ''

                            for value in data['detailItem']:
                                for salesman in value['salesmanList']:
                                    salesman_so = salesman['name']

                            value_rute = ''
                            print(data['toAddress'])
                            
                            if '#' in str(data['toAddress']):
                                value_rute = data['toAddress'][data['toAddress'].find("#"):]
                                print(value_rute)


                            formatted_data = {
                                'name': data['number'],
                                'date_order': ymd_date,
                                'item_accurate_id': data['id'],
                                'customer': data['customer']['name'],
                                'partner_id': int(data_cust),
                                'accurate_address': data['toAddress'],
                                'rute': value_rute.replace("#",""),
                                'has_been_invoiced': status,
                                'state': 'sale',
                                'salesman' : salesman_so
                            }

                            records_so_create.append(formatted_data)

                            existing_record = sale.search(
                                [('item_accurate_id', '=', data['id'])])

                            if not existing_record:
                                sale_order_data = sale.sudo().create(formatted_data)

                                for value in data['detailItem']:
                                    for salesman in value['salesmanList']:
                                        sale.write({
                                            'salesman': salesman['name']
                                        })

                                    product_id = product.search(
                                        [('item_accurate_id', '=', value['itemId'])], limit=1)
                                    item = {
                                        'product_id': product_id.id,
                                        'name': value['detailName'],
                                        'product_uom_qty': value['quantity'],
                                        'price_unit': value['unitPrice'],
                                        'order_id': sale_order_data.id,
                                        'tax_id': [(5, 0, 0)]
                                    }
                                    sale_order.sudo().create(item)

        return {
            'data': records_so_create
        }

    def get_receive_item_accurate(self, from_date, to_date):
        product = request.env['product.template']
        stock_picking = request.env['stock.picking']
        stock_move = request.env['stock.move']
        product_template_obj = request.env['product.product']
        vendor = request.env['res.partner']
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        url = f'https://zeus.accurate.id/accurate/api/receive-item/list.do?sp.pageSize=100&filter.transDate.op' \
              f'=BETWEEN&filter.transDate.val={from_date}&filter.transDate.val={to_date}'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }


        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            page_count = data['sp']['pageCount']
            for page in range(0, page_count):
                data_url = f"{url}&sp.page={page}"
                response_url = requests.get(data_url, headers=headers)
                items_url = response_url.json()['d']
                for item in items_url:
                    records_stock_picking_create = []
                    id_item = item['id']
                    url = f'https://zeus.accurate.id/accurate/api/receive-item/detail.do?id={int(id_item)}'

                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'X-Session-ID': session
                    }
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()['d']
                        vendor_id = vendor.search(
                            [('customer_accurate_id', '=', data['vendorId'])], limit=1)

                        formatted_data = {
                            'origin': data['number'],
                            'item_accurate_id': data['id'],
                            'partner_id': vendor_id,
                            'location_id': 14,
                            'location_dest_id': 8,
                            'picking_type_id' : 9,
                            'address_customer': data['toAddress'],
                            'state': 'assigned',
                        }

                        records_stock_picking_create.append(formatted_data)

                        existing_record = stock_picking.search(
                            [('item_accurate_id', '=', data['id'])])

                        if not existing_record:
                            stock_picking_obj = stock_picking.sudo().create(formatted_data)

                            for value in data['detailItem']:

                                product_id = product.search(
                                    [('item_accurate_id', '=', value['itemId'])], limit=1)

                                item = {
                                    'product_id': product_id.id,
                                    'name': value['detailName'],
                                    'product_uom': product_id.uom_id.id,
                                    'location_id': 14,
                                    'location_dest_id': 8,
                                    'product_uom_qty': value['quantity'],
                                    'price_unit': value['unitPrice'],
                                    'picking_id': stock_picking_obj.id,
                                }
                                stock_move.sudo().create(item)
                                stock_picking_obj.write({
                                    'state': 'assigned'
                                })



    def accurate_so_sync(self, id_so,id_so_accurate):
        access_token = self.get_access_token()['access_token']
        session = self.open_db_accurate(access_token)['session']
        product = request.env['product.template']
        print(access_token)
        print(session)
        sale_order_line = request.env['sale.order.line']
        url_item = f'https://zeus.accurate.id/accurate/api/sales-order/detail.do?id={id_so_accurate}'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Session-ID': session
        }

        sale_order = request.env['sale.order'].search([('id', '=', id_so)])

        if sale_order:
            response = requests.get(url_item, headers=headers)
            sale_order.action_cancel()
            sale_order.order_line.unlink()
            if response.status_code == 200:
                data = response.json()['d']
                for value in data['detailItem']:
                    product_id = product.search(
                        [('item_accurate_id', '=', value['itemId'])],limit=1)
                    item = {
                        'product_id': product_id.id,
                        'name': value['detailName'],
                        'product_uom_qty': value['quantity'],
                        'price_unit': value['unitPrice'],
                        'order_id': sale_order.id,
                        'tax_id': [(5, 0, 0)]
                    }
                    sale_order_line.sudo().create(item)

            sale_order.action_draft()
            sale_order.action_confirm()




class CustomReportController(http.Controller):
    @http.route('/custom_report_download/<int:record_id>/', type='http', auth="public")
    def custom_report_download(self, record_id, **kw):
        Model = request.env['rpb.rpb']
        record = Model.browse(record_id)

        if record:
            pdf_content = record._render_qweb_pdf([record.id])[0]
            file_name = f"{record.field_name_for_filename}.pdf"

            response = request.make_response(
                pdf_content,
                [('Content-Type', 'application/pdf')],
            )
            response.headers['Content-Disposition'] = http.content_disposition(file_name)

            return response
        else:
            return request.not_found()


