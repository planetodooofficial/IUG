Fix Error Blank Page In Window
==============================

On MS Windows, the mimetypes module relies on the Windows Registry to
guess mimetypes. As a consequence, when generating assets bundle for
javascript files, the mime type of js files may be wrong.

Installation
------------

Just install it.

Configuration
-------------

Nothing.

Usage
-----

**Try me on server.**

.. image:: https://homnaycodegi.com/wp-content/uploads/2017/11/tryme.png
   :alt: Try me on Server
   :target: https://odoo.homnaycodegi.com/vi_VN/

Known issues / Roadmap
----------------------

Updating.

Bug Tracker
-----------

If this module don't working. Please raise to me or you can fix it by two way.

**Firt way**

* Go to PGAdmin and run this query:

::

    UPDATE ir_attachment 
    SET mimetype = 'text/javascript' 
    WHERE mimetype ='text/plain' 
    and datas_fname like '%.js';

* Clear your browse cache, then F5 your browser.

After that, If you had error with displaying image and icon in Odoo

* Open cmd and paste pip install werkzeug --upgrade.
* Copy folder werkzeug in ``C:/Python27/Lib/site-packages`` (base on the path you install python).
* Paste it in folder ``C:/Program files (x86)/Odoo 10.0/server`` (base on the path you install Odoo).
* Apply for overwrite file. Reset Odoo services and F5 your browser.

**Second way**

* Replace method ``save_attachment`` in this module for module ``base`` 
in your Odoo directory.

Bugs are tracked on `MinhHQ Github Issues
<https://github.com/minhhq09/mhq-odoo-addons/issues>`_. 
In case of trouble, please check there if your issue has already been reported. 
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
-------

Contributors
^^^^^^^^^^^^

* MinhHQ <minh.hquang09@gmail.com>

Maintainer
^^^^^^^^^^

.. image:: https://homnaycodegi.com/wp-content/uploads/2017/07/cropped-download.png
   :alt: MinhHQ
   :target: https://homnaycodegi.com

This module is maintained by **MinhHQ**.
