from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    #browser.configure(slowmo=100)
    open_robot_order_website()
    orders = get_orders()

    for row in orders:
        fill_the_form(row)

    archive_receipts()

def open_robot_order_website():
    """Navigate to give URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    close_annoying_modal()

def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    return tables.read_table_from_csv("orders.csv", header=True)

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-" + str(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", str(order["Legs"]))
    page.fill("#address", str(order["Address"]))
    page.click("text=Preview")
    page.click("id=order")

    while page.locator(".alert.alert-danger").count() > 0: 
        page.click("id=order")

    screenshot = screenshot_robot(order["Order number"])
    receipt = store_receipt_as_pdf(order["Order number"])

    embed_screenshot_to_receipt(screenshot, receipt)

    page.click("text=Order another robot")
    
    close_annoying_modal()


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(receipt, pdf_path, margin=10)
    return pdf_path

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = f"output/receipts/pic{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path= pdf_file, output_path=pdf_file)


def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "zip_receipts.zip")

