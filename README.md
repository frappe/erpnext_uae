## ERPNext UAE

App to hold regional code for United Arab Emirates, built on top of ERPNext.

### Introduction

ERPNext UAE holds regional customizations for United Arab Emirates such as several custom fields for doctypes, print formats, reports like UAE VAT 201, doctypes for UAE VAT Settings. It is built on Frappe, a full-stack, meta-data driven, web framework, and integrates seamlessly with ERPNext, the most agile ERP software.


### Installation

Using bench, [install ERPNext](https://github.com/frappe/bench#installation) as mentioned here.

Once ERPNext is installed, add ERPNext UAE app to your bench by running

```sh
$ bench get-app https://github.com/frappe/erpnext_uae.git
```

After that, you can install the app on required site (let's say demo.com )by running

```sh
$ bench --site demo.com install-app erpnext_uae
```

### License

GNU GPL V3. See [license.txt](https://github.com/frappe/erpnext_uae/blob/develop/license.txt) for more information.
