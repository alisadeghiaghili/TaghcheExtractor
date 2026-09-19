# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 17:53:49 2023

@author: sadeghi.a
"""

import os
import sys
import base64
import random
import time
import io
from PIL import Image, ImageFont, ImageDraw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QProgressBar, QFileDialog, QLineEdit, QMessageBox

class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.app_height = 1000 + 219
        self.app_width = 750 + 12

        self.original_margin_left = 26
        self.original_margin_top = 21
        self.original_margin_right = 29
        self.original_margin_bottom = 11

        self.additional_margin_left = 10
        self.additional_margin_top = 10
        self.additional_margin_right = 10
        self.additional_margin_bottom = 10
        
        self.geckodriver_path = self._resolve_geckodriver()
        self.output_dir = r'D:\Taghche\book'
        self.progress_label = QLabel('', self)
        self.initUI()

    @classmethod
    def _resolve_geckodriver(cls):
        """Prefer a bundled geckodriver, then one next to the app, then let
        Selenium Manager find one."""
        candidates = []
        if getattr(sys, 'frozen', False):
            # A --onefile exe extracts bundled data to a temp dir at runtime.
            meipass = getattr(sys, '_MEIPASS', '')
            if meipass:
                candidates.append(os.path.join(meipass, 'geckodriver.exe'))
            candidates.append(os.path.join(os.path.dirname(sys.executable),
                                           'geckodriver.exe'))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(script_dir, 'geckodriver.exe'))
        candidates.append(r'./geckodriver.exe')
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return r'./geckodriver.exe'  # fallback -> Selenium Manager

    def initUI(self):
        self.setGeometry(100, 100, 400, 100)
        self.setWindowTitle('Screenshot App')

        margin_layout = QHBoxLayout()
        margin_label = QLabel('Additional Margins:', self)
        margin_layout.addWidget(margin_label)

        margin_layout.addWidget(QLabel('Left:', self))
        self.margin_left_spinbox = QSpinBox(self)
        self.margin_left_spinbox.setRange(0, 100)
        self.margin_left_spinbox.setValue(self.additional_margin_left)
        margin_layout.addWidget(self.margin_left_spinbox)

        margin_layout.addWidget(QLabel('Top:', self))
        self.margin_top_spinbox = QSpinBox(self)
        self.margin_top_spinbox.setRange(0, 100)
        self.margin_top_spinbox.setValue(self.additional_margin_top)
        margin_layout.addWidget(self.margin_top_spinbox)

        margin_layout.addWidget(QLabel('Right:', self))
        self.margin_right_spinbox = QSpinBox(self)
        self.margin_right_spinbox.setRange(0, 100)
        self.margin_right_spinbox.setValue(self.additional_margin_right)
        margin_layout.addWidget(self.margin_right_spinbox)

        margin_layout.addWidget(QLabel('Bottom:', self))
        self.margin_bottom_spinbox = QSpinBox(self)
        self.margin_bottom_spinbox.setRange(0, 100)
        self.margin_bottom_spinbox.setValue(self.additional_margin_bottom)
        margin_layout.addWidget(self.margin_bottom_spinbox)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('Output folder:', self))
        self.output_dir_edit = QLineEdit(self)
        self.output_dir_edit.setText(self.output_dir)
        self.output_dir_edit.setMinimumWidth(180)
        output_layout.addWidget(self.output_dir_edit)
        browse_button = QPushButton('Browse...', self)
        browse_button.clicked.connect(self.choose_output_dir)
        output_layout.addWidget(browse_button)

        height_width_layout = QHBoxLayout()

        height_width_layout.addWidget(QLabel('Height:', self))
        self.height_spinbox = QSpinBox(self)
        self.height_spinbox.setRange(0, 2000)
        self.height_spinbox.setValue(self.app_height)
        height_width_layout.addWidget(self.height_spinbox)

        height_width_layout.addWidget(QLabel('Width:', self))
        self.width_spinbox = QSpinBox(self)
        self.width_spinbox.setRange(0, 2000)
        self.width_spinbox.setValue(self.app_width)
        height_width_layout.addWidget(self.width_spinbox)

        main_layout = QVBoxLayout()
        main_layout.addLayout(margin_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(height_width_layout)

        button_layout = QHBoxLayout()
        self.capture_button = QPushButton('Capture', self)
        self.capture_button.clicked.connect(self.capture_screenshots)
        button_layout.addWidget(self.capture_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

        self.show()

    def choose_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, 'Choose output folder', self.output_dir_edit.text())
        if directory:
            self.output_dir_edit.setText(directory)


    def capture_screenshots(self):
        self.output_dir = self.output_dir_edit.text().strip() or self.output_dir

        self.additional_margin_left = self.margin_left_spinbox.value()
        self.additional_margin_top = self.margin_top_spinbox.value()
        self.additional_margin_right = self.margin_right_spinbox.value()
        self.additional_margin_bottom = self.margin_bottom_spinbox.value()

        self.app_height = self.height_spinbox.value()
        self.app_width = self.width_spinbox.value()

        blink = "https://taaghche.com/"

        os.makedirs(self.output_dir, exist_ok=True)

        imagelist = []
        driver = None
        try:
            # Use an explicit geckodriver if present; otherwise let Selenium
            # Manager locate/download a compatible one.
            service = (Service(self.geckodriver_path)
                       if os.path.exists(self.geckodriver_path)
                       else Service())
            driver = webdriver.Firefox(service=service)
            driver.set_window_size(self.app_width + self.original_margin_left + self.original_margin_right + self.additional_margin_left + self.additional_margin_right,
                                   self.app_height + self.original_margin_top + self.original_margin_bottom + self.additional_margin_top + self.additional_margin_bottom)
            driver.get(blink)
            time.sleep(5)
            try:
                total_pages = int(driver.find_element(By.CSS_SELECTOR, '#totalPages').text)
            except NoSuchElementException:
                time.sleep(20)
                total_pages = int(driver.find_element(By.CSS_SELECTOR, '#totalPages').text)

            for this_page in range(total_pages + 1): # + 25):
                time.sleep(random.uniform(0, 5))

                if this_page % 25 == 0:
                    time.sleep(15)

                self.take_screenshot(driver, this_page)

                image_path = os.path.join(self.output_dir, f'{this_page}.png')
                imagelist.append(Image.open(image_path))

                progress = int((this_page + 1) / (total_pages + 1) * 100)# + 25) * 100)
                self.progress_bar.setValue(progress)

                remaining_pages = total_pages - this_page
                time_remaining = int(remaining_pages * 5)  # Assuming 5 seconds per page
                minutes_remaining = time_remaining // 60
                seconds_remaining = time_remaining % 60
                eta_text = f"ETA: {minutes_remaining} min {seconds_remaining} sec"
                self.progress_label.setText(eta_text)
                QApplication.processEvents()

                # Only navigate to the next page if there is one left.
                if this_page != total_pages:
                    driver.find_element(By.ID, '___nextPageMobile').click()

            # Build the PDF once, after all pages are captured.
            imagelist[0].save(
                os.path.join(self.output_dir, 'result.pdf'),
                save_all=True,
                append_images=imagelist[1:],
                resolution=300.0,  # Adjust this DPI value as needed
                quality=95  # You can also adjust the quality
            )

            # Release file handles now that everything is written.
            for img in imagelist:
                img.close()

            self.progress_label.setText('Done.')
        except Exception as e:
            self.progress_label.setText('Error')
            QMessageBox.critical(
                self, 'Capture failed',
                f'Something went wrong:\n\n{e}')
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass


    def take_screenshot(self, driver, page_number):
        canvas = driver.find_element(By.CSS_SELECTOR, "#canvas0")
        canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
        canvas_png = base64.b64decode(canvas_base64)

        image = Image.open(io.BytesIO(canvas_png))
        image.load()
        width, height = image.size
        left = self.original_margin_left - self.additional_margin_left
        top = self.original_margin_top - self.additional_margin_top
        right = width + self.additional_margin_right
        bottom = height + self.additional_margin_bottom

        # Create a new image with a white background
        background = Image.new("RGB", (right - left, bottom - top), (255, 255, 255))
        background.paste(image, (self.additional_margin_left - left, self.additional_margin_top - top), mask=image.split()[3])

        # Draw the page number onto the (still RGB) background.
        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default()
        page_number_text = f"{page_number}"
        text_left, text_top, text_right, text_bottom = draw.textbbox((0, 0), page_number_text, font=font)
        text_width = text_right - text_left
        text_height = text_bottom - text_top
        text_x = (right - left - text_width) // 2
        text_y = bottom - top - text_height
        draw.text((text_x, text_y), page_number_text, fill=(0, 0, 0), font=font)

        # Convert to grayscale only after the text is drawn, so the
        # page number is preserved in the output.
        grayscale_image = background.convert("L")

        # Save the grayscale image with a white background.
        image_path = os.path.join(self.output_dir, f'{page_number}.png')
        grayscale_image.save(image_path, dpi=(300, 300))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenshotApp()
    sys.exit(app.exec_())

