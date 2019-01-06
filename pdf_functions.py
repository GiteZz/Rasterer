import PyPDF2
from wand.image import Image
import io
import os
import numpy as np
import PIL

# Used from the internet, not the cleanest should be rewritten
def pdf_page_to_png(src_pdf, pagenum = 0, resolution = 200,):
    """
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """
    dst_pdf = PyPDF2.PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(pagenum))

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file = pdf_bytes, resolution = resolution)
    img.convert("png")

    img_buffer = np.asarray(bytearray(img.make_blob(format='png')), dtype='uint8')
    bytesio = io.BytesIO(img_buffer)
    pil_img = PIL.Image.open(bytesio).convert('RGB')

    return pil_img