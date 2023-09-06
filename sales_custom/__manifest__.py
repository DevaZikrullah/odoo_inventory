{
    'name' : 'Custom Sale HIJ',
    'description': """
        Custome Sale
    """,
    "depends": ["sale","product","purchase","stock","base","fleet","digest"],
    'category': 'custom HIJ',
    'data': [
        'views/sale_quot_views.xml',
        'wizard/trans_date_view.xml',
        'views/fleet_views.xml',
        'wizard/delivered_view.xml',
        'wizard/rpb_views.xml',
        'views/product_template_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'sales_custom/static/src/js/update_accurate_button.js',
        ],
        'web.assets_qweb': [
            'sales_custom/static/src/xml/update_accurate_button.xml',
        ],
    },
}
