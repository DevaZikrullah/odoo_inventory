odoo.define('button_near_in_create.tree_button', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t; // Define the _t function in the current context

    var TreeButton = ListController.extend({
        buttons_template: 'button_near_in_create.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .open_wizard_action': '_OpenWizard',
        }),
        _OpenWizard: function () {
            var self = this;

            // Display a confirmation dialog before updating the data
            Dialog.confirm(this, _t("Are you sure you want to update the data?"), {
                confirm_callback: function () {
                    console.log('Button clicked!'); // Log the button click

                    // Use the 'ajax' method to call the custom API endpoint
                    self._rpc({
                        route: '/api/accurate',
                        params: {},
                    })
                    .then(function(result) {
                        if ('data' in result) {
                            var itemsPerPage = 10; // Number of items to display per page
                            var currentPage = 1;
                            var totalItems = result.data.item.length;

                            // Show the custom modal dialog
                            var modal = document.createElement('div');
                            modal.className = 'modal';

                            var modalContent = document.createElement('div');
                            modalContent.className = 'modal-content';

                            // Center the modal content vertically and horizontally
                            modalContent.style.margin = 'auto';
                            modalContent.style.position = 'absolute';
                            modalContent.style.left = 0;
                            modalContent.style.right = 0;
                            modalContent.style.top = '50%';
                            modalContent.style.transform = 'translateY(-50%)';
                            modalContent.style.msTransform = 'translateY(-50%)';

                            var closeButton = document.createElement('span');
                            closeButton.className = 'close';
                            closeButton.innerHTML = '&times;';

                            // Close the modal when the close button is clicked
                            closeButton.onclick = function() {
                                modal.style.display = 'none';
                            };

                            var modalData = document.createElement('div');
                            modalData.id = 'modal-data';
                            modalData.style.maxHeight = '80%'; // Set the maximum height for the scrollable content

                            var table = document.createElement('table');
                            table.id = 'modal-table';
                            table.style.width = '100%';
                            table.style.borderCollapse = 'collapse';
                            table.innerHTML = '<tr><th>Item ID</th><th>Item Name</th><th>Item Number</th></tr>';

                            function displayItems(page) {
                                table.innerHTML = '<tr><th>Item ID</th><th>Item Name</th><th>Item Number</th></tr>';
                                var startIndex = (page - 1) * itemsPerPage;
                                var endIndex = Math.min(startIndex + itemsPerPage, totalItems);

                                for (var i = startIndex; i < endIndex; i++) {
                                    var item = result.data.item[i];
                                    var row = table.insertRow();
                                    row.innerHTML = '<td>' + item['Item ID'] + '</td><td>' + item['Item Name'] + '</td><td>' + item['Item Number'] + '</td>';
                                }
                            }

                            displayItems(currentPage);

                            var nextPageButton = document.createElement('button');
                            nextPageButton.innerHTML = 'Next Page';

                            nextPageButton.onclick = function() {
                                currentPage++;
                                displayItems(currentPage);
                            };

                            modalData.appendChild(table);
                            modalContent.appendChild(closeButton);
                            modalContent.appendChild(modalData);
                            modalContent.appendChild(nextPageButton);
                            modal.appendChild(modalContent);

                            // Append the modal to the body
                            document.body.appendChild(modal);

                            // Open the modal when the dialog is clicked
                            modal.style.display = 'block';
                        } else {
                            // Show an error message if data fetch fails
                            alert('Error: Failed to fetch data.');
                        }
                    });
                },
            });
        }
    });

    var SaleOrderListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });

    viewRegistry.add('button_in_tree', SaleOrderListView);
});
