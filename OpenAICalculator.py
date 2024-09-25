from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QLineEdit, QLabel, QDialog, QFormLayout, QDialogButtonBox,
    QScrollArea, QVBoxLayout
)
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont
from openai import OpenAI

# Initialize OpenAI with API key
client = OpenAI(api_key='your-api-key-here')

def query_openai(expression, explain=False):
    """
    Query OpenAI API to calculate or explain math expression

    :param expression: Expression to evaluate
    :param explain: If true, request explanation for result

    :return: Response (result or explanation) from OpenAI
    """
    if explain:
        prompt = f"Explain the following result step by step: {expression}"
    else:
        prompt = f"Calculate the following and return only the result, without any additional explanation or text: {expression}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()   # Return cleaned response
    except Exception as e:
        return f"Error: {str(e)}"   # Return error if exception


class IntegralDialog(QDialog):
    """
    Dialog for entering integral details
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Integral Details")   # Dialog title
        self.setModal(True)   # Make dailog modal
        self._set_styles()   # Apply styles to dialog
        self._setup_layout()   # Set layout of dialog

    def _set_styles(self):
        """
        Set styles for dialog and components
        """
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

    def _setup_layout(self):
        """
        Set layout for integral dialog
        """
        layout = QFormLayout()   # Create form layout
        self.function_entry = QLineEdit()   # Function input
        self.lower_limit_entry = QLineEdit()   # Lower limit input
        self.upper_limit_entry = QLineEdit()   # Upper limit input

        # Add rows to layout
        layout.addRow("Function:", self.function_entry)
        layout.addRow("Lower Limit:", self.lower_limit_entry)
        layout.addRow("Upper Limit:", self.upper_limit_entry)

        # Create buttons for accepting or cancelling dialog
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Add button box to layout
        layout.addWidget(self.button_box)

        # Set layout for dialog
        self.setLayout(layout)

    def get_values(self):
        """
        Retrieve values from dialog input
        """
        return (self.function_entry.text(), self.lower_limit_entry.text(), self.upper_limit_entry.text())   # Return function and limits


class Calculator(QMainWindow):
    """
    Main calculator window for calculations and displaying result
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenAI Calculator")   # Set window title
        self.setGeometry(100, 100, 400, 500)   # Set initial window size and position
        self._set_styles()   # Apply styles to window
        self._setup_ui()   # Set UI

    def _set_styles(self):
        """
        Set styles for main window and components
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLineEdit, QLabel {
                background-color: #34495e;
                color: #ecf0f1;
                border: none;
                padding: 10px;
                font-size: 18px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#equalButton {
                background-color: #e74c3c;
            }
            QPushButton#equalButton:hover {
                background-color: #c0392b;
            }
            QPushButton#operatorButton {
                background-color: #f39c12;
            }
            QPushButton#operatorButton:hover {
                background-color: #d35400;
            }
            QPushButton#functionButton {
                background-color: #27ae60;
            }
            QPushButton#functionButton:hover {
                background-color: #2ecc71;
            }
            QScrollArea {
                background-color: #2c3e50;
                border: none;
            }
        """)

    def _setup_ui(self):
        """
        Set UI for calculator
        """
        central_widget = QWidget()   # Central widget for main window
        self.setCentralWidget(central_widget)   # Set central widget

        # For user input
        self.entry = QLineEdit()
        self.entry.setAlignment(Qt.AlignRight)
        self.entry.setFont(QFont('Arial', 20))

        # Create scroll area to display results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)   # Resize widget with scroll area
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   # Disable horizontal scroll bar

        self.result_widget = self._create_result_widget()   # Create widget to display results
        self.scroll_area.setWidget(self.result_widget)   # Set result widget in scroll area

        # Button for Explain Me
        self.explain_button = QPushButton("Explain Me")
        self.explain_button.setEnabled(False)   # Initially disable button
        self.explain_button.clicked.connect(self.explain_result)   # Connect button click to explanation function
        self.update_explain_button_style()   # Update button style based on state

        # Main layout for calculator
        main_layout = QVBoxLayout()
        button_layout = self._create_button_layout()   # Create layout for calculator buttons

        # Add components to main layour
        main_layout.addWidget(self.entry)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.explain_button)
        main_layout.addLayout(button_layout)

        main_layout.setContentsMargins(QMargins(20, 20, 20, 20))   # Set margins for main layout
        central_widget.setLayout(main_layout)   # Set layout for central widget

    def _create_result_widget(self):
        """
        Create widget to display calculation results
        """
        result_widget = QWidget()   # Create new widget for results
        result_layout = QVBoxLayout()   # Vertical layout for results
        self.result_label = QLabel("Result")
        self.result_label.setAlignment(Qt.AlignRight)
        self.result_label.setFont(QFont('Arial', 16))
        result_layout.addWidget(self.result_label)
        result_widget.setLayout(result_layout)
        self.result_label.setWordWrap(True)
        result_widget.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border: none;
            }
        """)
        return result_widget

    def _create_button_layout(self):
        """
        Create layout for calculator buttons
        """
        # Create grid layout
        button_layout = QGridLayout()
        button_layout.setSpacing(10)

        button_configs = [
            ('∫', 'integral', 'functionButton'), ('(', '(', 'operatorButton'), (')', ')', 'operatorButton'), ('^', '^', 'operatorButton'), ('C', 'clear', 'operatorButton'),
            ('sin', 'sin(', 'functionButton'), ('7', '7'), ('8', '8'), ('9', '9'), ('/', '/', 'operatorButton'),
            ('cos', 'cos(', 'functionButton'), ('4', '4'), ('5', '5'), ('6', '6'), ('*', '*', 'operatorButton'),
            ('tan', 'tan(', 'functionButton'), ('1', '1'), ('2', '2'), ('3', '3'), ('-', '-', 'operatorButton'),
            ('log', 'log(', 'functionButton'), ('0', '0'), ('.', '.'), ('=', 'evaluate', 'equalButton'), ('+', '+', 'operatorButton'),
        ]

        # Create buttons and add to layout
        for i, (text, action, *style) in enumerate(button_configs):
            button = QPushButton(text)
            if style:
                button.setObjectName(style[0])
            button.clicked.connect(lambda _, a=action: self.handle_button_click(a))
            row, col = divmod(i, 5)
            button_layout.addWidget(button, row, col)

        return button_layout   # Return layout with buttons

    def handle_button_click(self, action):
        """
        Handles button click events for number and operator

        :param action: text of button clicked
        """
        if action == 'clear':
            self.clear_entry()   # Clear entry if C clicked
        elif action == 'evaluate':
            self.evaluate_expression()   # Evaluate if = clicked
        elif action == 'integral':
            self.show_integral_popup()   # Show the integral popup if integral clicked
        else:
            self.entry.setText(self.entry.text() + action)   # Append button text to entry

    def clear_entry(self):
        """
        Clears calculator entry
        """
        self.entry.clear()   # Clear text in entry field
        self.result_label.setText("Result")   # Reset result to Result
        self.explain_button.setEnabled(False)   # Disable Explain button
        self.update_explain_button_style()   # Update style of Explain button

    def evaluate_expression(self):
        """
        Evaluates expression entered by user using OpenAI API
        """
        # Get expression from entry field
        expression = self.entry.text()

        if expression:
            result = query_openai(expression)   # Query OpenAI API for result
            self.result_label.setText(f"Result: {result}")   # Update result label with result
            self.explain_button.setEnabled(True)   # Enable Explain button
            self.update_explain_button_style()   # Update style of Explain button
        else:
            self.result_label.setText("Please enter an expression.")   # Prompt user if no expression entered

    def explain_result(self):
        """
        Explains result of the result using OpenAI API
        """
        # Get expression from entry field
        expression = self.entry.text()

        if expression:
            explanation = query_openai(expression, explain=True)   # Query OpenAI API for result
            self.result_label.setText(f"Explanation: {explanation}")   # Update result label with explanation
        else:
            self.result_label.setText("Please enter an expression.")   # Prompt user if no expression entered

    def show_integral_popup(self):
        """
        Opens dialog for integral popu
        """
        # Open dialog
        dialog = IntegralDialog(self)

        # Check if dialog accepted
        if dialog.exec_() == QDialog.Accepted:
            function, lower_limit, upper_limit = dialog.get_values()   # Get integral inputs from dialog
            integral_expression = f"∫({function}) from {lower_limit} to {upper_limit}"   # Format integral expression
            result = query_openai(integral_expression)   # Query OpenAI API for integral result
            self.result_label.setText(f"Integral Result: {result}")   # Update result label with integral result
            self.explain_button.setEnabled(True)   # Enable Explain button
            self.update_explain_button_style()   # Update style of Explain button

    def update_explain_button_style(self):
        """
        Update Explain button style based on whether enabled or disabled
        """
        if self.explain_button.isEnabled():
            self.explain_button.setStyleSheet("background-color: #2980b9;")
        else:
            self.explain_button.setStyleSheet("background-color: #7f8c8d;")

if __name__ == "__main__":
    app = QApplication([])   # Create Qt application
    window = Calculator()   # Instantiate calculator window
    window.show()   # Show calculator window
    app.exec_()   # Execute Qt application loop
