#!/usr/bin/env python
import os

from inventory_api.app import app

if __name__ == '__main__':
    port = os.environ['INVENTORY_API_PORT']
    app.run(host='localhost', port=port)
