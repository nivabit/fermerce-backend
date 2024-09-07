from deta import Deta  # Import Deta
from fermerce.core.settings import config

deta = Deta(config.deta_space_key)

product_drive = deta.Drive("product_drive")
vendor_drive = deta.Drive("vendor_drive")
