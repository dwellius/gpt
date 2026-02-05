"""Главное окно GUI экспертной системы (PySide6)."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from app.db.database import init_db, save_history
from app.es.engine import ExpertSystem, load_default_rules


BRAND_MODELS = {
    "LADA": ["Granta", "Vesta", "Niva", "XRAY"],
    "KIA": ["Rio", "Ceed", "Sportage", "Sorento"],
    "Hyundai": ["Solaris", "Elantra", "Tucson", "Santa Fe"],
    "Volkswagen": ["Polo", "Golf", "Passat", "Tiguan"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Land Cruiser"],
    "Skoda": ["Octavia", "Rapid", "Kodiaq", "Superb"],
    "BMW": ["3 Series", "5 Series", "X3", "X5"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLA", "GLE"],
    "Audi": ["A4", "A6", "Q5", "Q7"],
    "Nissan": ["Qashqai", "X-Trail", "Almera", "Juke"],
    "Ford": ["Focus", "Mondeo", "Kuga", "Fiesta"],
    "Chevrolet": ["Cruze", "Aveo", "Niva", "Captiva"],
    "Renault": ["Logan", "Duster", "Kaptur", "Sandero"],
    "Другое": [],
}


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно с многошаговым опросом."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Экспертная система диагностики автомобиля")
        self.setMinimumSize(900, 700)

        # Инициализация БД и экспертной системы.
        init_db()
        self.engine = ExpertSystem(load_default_rules())

        # Центральный виджет.
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QtWidgets.QVBoxLayout(central_widget)

        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)

        # Шаг 1: общая информация об авто.
        self.general_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.general_tab, "Общие данные")
        self._build_general_tab()

        # Шаг 2: условия появления проблемы.
        self.conditions_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.conditions_tab, "Условия")
        self._build_conditions_tab()

        # Шаг 3: симптомы.
        self.symptoms_tab = QtWidgets.QScrollArea()
        self.symptoms_tab.setWidgetResizable(True)
        self.tabs.addTab(self.symptoms_tab, "Симптомы")
        self._build_symptoms_tab()

        # Шаг 4: дополнительная информация.
        self.additional_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.additional_tab, "Доп. информация")
        self._build_additional_tab()

        # Кнопки управления.
        controls = QtWidgets.QHBoxLayout()
        self.layout.addLayout(controls)

        self.start_button = QtWidgets.QPushButton("Начать диагностику")
        self.start_button.clicked.connect(self.reset_form)
        controls.addWidget(self.start_button)

        self.diagnose_button = QtWidgets.QPushButton("Получить диагноз")
        self.diagnose_button.clicked.connect(self.run_diagnosis)
        controls.addWidget(self.diagnose_button)

        self.result_box = QtWidgets.QGroupBox("Результат диагностики")
        self.layout.addWidget(self.result_box)
        self._build_result_box()

    def _build_general_tab(self) -> None:
        """Создать элементы шага с информацией об автомобиле."""
        layout = QtWidgets.QFormLayout(self.general_tab)

        self.brand_label = QtWidgets.QLabel("Марка:*")
        self.brand_combo = QtWidgets.QComboBox()
        self.brand_combo.addItems(BRAND_MODELS.keys())
        self.brand_combo.currentTextChanged.connect(self._update_model_completer)
        layout.addRow(self.brand_label, self.brand_combo)

        self.model_label = QtWidgets.QLabel("Модель:*")
        self.model_edit = QtWidgets.QLineEdit()
        layout.addRow(self.model_label, self.model_edit)

        self.year_label = QtWidgets.QLabel("Год выпуска:*")
        self.year_combo = QtWidgets.QComboBox()
        self.year_combo.addItems([str(year) for year in range(1990, 2026)])
        layout.addRow(self.year_label, self.year_combo)

        self.mileage_label = QtWidgets.QLabel("Пробег:*")
        self.mileage_spin = QtWidgets.QSpinBox()
        self.mileage_spin.setRange(0, 999)
        self.mileage_spin.setSuffix(" тыс. км")
        layout.addRow(self.mileage_label, self.mileage_spin)

        # Инициализируем автодополнение для модели.
        self._update_model_completer(self.brand_combo.currentText())

    def _update_model_completer(self, brand: str) -> None:
        """Обновить автодополнение моделей по выбранной марке."""
        models = BRAND_MODELS.get(brand, [])
        completer = QtWidgets.QCompleter(models)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.model_edit.setCompleter(completer)

    def _build_conditions_tab(self) -> None:
        """Создать чекбоксы условий появления проблемы."""
        layout = QtWidgets.QVBoxLayout(self.conditions_tab)
        self.condition_checks = []

        conditions = [
            "На холодном двигателе",
            "На прогретом двигателе",
            "На высоких оборотах",
            "На холостом ходу",
            "При разгоне",
            "При торможении",
            "На неровной дороге",
            "В сырую погоду",
            "Постоянно",
        ]

        for text in conditions:
            checkbox = QtWidgets.QCheckBox(text)
            layout.addWidget(checkbox)
            self.condition_checks.append(checkbox)

        layout.addStretch()

    def _build_symptoms_tab(self) -> None:
        """Собрать вкладку симптомов с группировкой по системам."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        self.symptom_checks: list[QtWidgets.QAbstractButton] = []

        layout.addWidget(self._create_symptom_group(
            "Двигатель и выхлоп",
            [
                "Нет проблем",
                "Не заводится (стартер не крутит)",
                "Не заводится (стартер крутит)",
                "Заводится и глохнет",
                "Троит",
                "Потеря мощности",
                "Дёргается",
                "Повышенный расход топлива",
                "Посторонние звуки",
            ],
        ))

        # Цвет дыма — отдельный выбор.
        smoke_layout = QtWidgets.QHBoxLayout()
        smoke_label = QtWidgets.QLabel("Цвет дыма:")
        self.smoke_combo = QtWidgets.QComboBox()
        self.smoke_combo.addItems(["Не указан", "Белый", "Синий", "Чёрный"])
        smoke_layout.addWidget(smoke_label)
        smoke_layout.addWidget(self.smoke_combo)
        smoke_layout.addStretch()
        layout.addLayout(smoke_layout)

        layout.addWidget(self._create_symptom_group(
            "Ходовая и рулевое",
            [
                "Нет проблем",
                "Стук на кочках",
                "Скрип при повороте руля",
                "Уводит в сторону",
                "Люфт руля",
                "Вибрация на скорости",
            ],
        ))
        layout.addWidget(self._create_symptom_group(
            "Тормозная система",
            [
                "Нет проблем",
                "Скрип при торможении",
                "Мягкая педаль",
                "Увеличенный ход педали",
                "Увод при торможении",
                "Стук при нажатии",
            ],
        ))
        layout.addWidget(self._create_symptom_group(
            "Электрооборудование",
            [
                "Нет проблем",
                "Не работают фары / поворотники / стоп-сигналы",
                "Не работают стеклоподъёмники / дворники",
                "Проблемы мультимедиа",
                "Сбои приборной панели",
                "Быстро разряжается аккумулятор",
            ],
        ))
        layout.addWidget(self._create_symptom_group(
            "Внешние признаки",
            [
                "Нет",
                "Подтёки масла",
                "Подтёки антифриза",
                "Подтёки тормозной жидкости",
                "Подтёки топлива",
                "Запахи",
            ],
        ))
        layout.addWidget(self._create_symptom_group(
            "Индикация панели приборов",
            [
                "Ничего не горит",
                "Check Engine",
                "Аккумулятор",
                "Давление масла",
                "Температура ОЖ",
                "ABS / ESP",
            ],
        ))

        # Свободный текст для "Другое".
        other_layout = QtWidgets.QHBoxLayout()
        other_label = QtWidgets.QLabel("Другое (текст):")
        self.other_indicator_edit = QtWidgets.QLineEdit()
        other_layout.addWidget(other_label)
        other_layout.addWidget(self.other_indicator_edit)
        layout.addLayout(other_layout)

        layout.addStretch()
        self.symptoms_tab.setWidget(container)

    def _create_symptom_group(self, title: str, items: list[str]) -> QtWidgets.QGroupBox:
        """Создать группу чекбоксов для симптомов."""
        group = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout(group)
        for item in items:
            checkbox = QtWidgets.QCheckBox(item)
            group_layout.addWidget(checkbox)
            self.symptom_checks.append(checkbox)
        return group

    def _build_additional_tab(self) -> None:
        """Сформировать вкладку дополнительной информации."""
        layout = QtWidgets.QFormLayout(self.additional_tab)

        self.repair_history_edit = QtWidgets.QTextEdit()
        layout.addRow("История недавних ремонтов:", self.repair_history_edit)

        self.self_repair_edit = QtWidgets.QTextEdit()
        layout.addRow("Попытки самостоятельного ремонта:", self.self_repair_edit)

        self.noise_character_edit = QtWidgets.QTextEdit()
        layout.addRow("Характер стука/шума:", self.noise_character_edit)

        self.symptom_change_edit = QtWidgets.QTextEdit()
        layout.addRow("Изменение симптомов при прогреве:", self.symptom_change_edit)

    def _build_result_box(self) -> None:
        """Подготовить блок вывода результата диагностики."""
        layout = QtWidgets.QVBoxLayout(self.result_box)

        self.result_label = QtWidgets.QLabel("Диагноз: -")
        self.probability_label = QtWidgets.QLabel("Вероятность: -")
        self.node_label = QtWidgets.QLabel("Узел: -")
        self.recommendations_list = QtWidgets.QListWidget()

        layout.addWidget(self.result_label)
        layout.addWidget(self.probability_label)
        layout.addWidget(self.node_label)
        layout.addWidget(QtWidgets.QLabel("Рекомендации:"))
        layout.addWidget(self.recommendations_list)

    def _collect_symptoms(self) -> set[str]:
        """Собрать выбранные симптомы из интерфейса."""
        selected = {box.text() for box in self.symptom_checks if box.isChecked()}
        selected.update({box.text() for box in self.condition_checks if box.isChecked()})

        smoke = self.smoke_combo.currentText()
        if smoke != "Не указан":
            selected.add(f"Цвет дыма: {smoke}")

        other_text = self.other_indicator_edit.text().strip()
        if other_text:
            selected.add(other_text)

        return selected

    def _collect_car_info(self) -> dict[str, str | int]:
        """Собрать информацию об автомобиле."""
        return {
            "brand": self.brand_combo.currentText(),
            "model": self.model_edit.text().strip(),
            "year": int(self.year_combo.currentText()),
            "mileage": self.mileage_spin.value(),
        }

    def reset_form(self) -> None:
        """Сбросить все поля ввода для новой диагностики."""
        self.model_edit.clear()
        self.year_combo.setCurrentIndex(0)
        self.mileage_spin.setValue(0)
        for checkbox in self.condition_checks:
            checkbox.setChecked(False)
        for checkbox in self.symptom_checks:
            checkbox.setChecked(False)
        self.smoke_combo.setCurrentIndex(0)
        self.other_indicator_edit.clear()
        self.repair_history_edit.clear()
        self.self_repair_edit.clear()
        self.noise_character_edit.clear()
        self.symptom_change_edit.clear()
        self._mark_required_label(self.brand_label, True)
        self._mark_required_label(self.model_label, True)
        self._mark_required_label(self.year_label, True)
        self._mark_required_label(self.mileage_label, True)
        self._set_result(
            diagnosis="-",
            probability="-",
            node="-",
            recommendations=[],
        )
        self.tabs.setCurrentIndex(0)

    def run_diagnosis(self) -> None:
        """Запустить диагностику и вывести результат."""
        if not self._validate_required_fields():
            return

        symptoms = self._collect_symptoms()
        if not symptoms:
            QtWidgets.QMessageBox.warning(
                self,
                "Недостаточно данных",
                "Выберите хотя бы один симптом или условие появления проблемы.",
            )
            return
        car_info = self._collect_car_info()

        # Дополняем симптомы дополнительными сведениями для контекста.
        for label, text in [
            ("История ремонтов", self.repair_history_edit.toPlainText()),
            ("Самостоятельный ремонт", self.self_repair_edit.toPlainText()),
            ("Характер шума", self.noise_character_edit.toPlainText()),
            ("Изменение симптомов", self.symptom_change_edit.toPlainText()),
        ]:
            cleaned = text.strip()
            if cleaned:
                symptoms.add(f"{label}: {cleaned}")

        result = self.engine.diagnose(symptoms)
        self._set_result(
            diagnosis=result["diagnosis"],
            probability=f"{result['probability']}%",
            node=result["node"],
            recommendations=result["recommendations"],
        )

        # Сохраняем историю в БД.
        save_history(car_info, sorted(symptoms), result)

    def _validate_required_fields(self) -> bool:
        """Проверить заполнение обязательных полей."""
        missing = []
        self._mark_required_label(self.model_label, True)
        self._mark_required_label(self.brand_label, True)
        self._mark_required_label(self.year_label, True)
        self._mark_required_label(self.mileage_label, True)

        if not self.model_edit.text().strip():
            missing.append("Модель")
            self._mark_required_label(self.model_label, False)

        if not self.brand_combo.currentText():
            missing.append("Марка")
            self._mark_required_label(self.brand_label, False)

        if not self.year_combo.currentText():
            missing.append("Год выпуска")
            self._mark_required_label(self.year_label, False)

        if self.mileage_spin.value() == 0:
            missing.append("Пробег")
            self._mark_required_label(self.mileage_label, False)

        if missing:
            QtWidgets.QMessageBox.warning(
                self,
                "Обязательные поля",
                "Заполните обязательные поля: "
                + ", ".join(missing)
                + ". Поля подсвечены красным.",
            )
            return False

        return True

    @staticmethod
    def _mark_required_label(label: QtWidgets.QLabel, is_valid: bool) -> None:
        """Подсветить обязательное поле, если оно не заполнено."""
        if is_valid:
            label.setStyleSheet("color: #2c3e50;")
        else:
            label.setStyleSheet("color: #c0392b; font-weight: bold;")

    def _set_result(
        self,
        diagnosis: str,
        probability: str,
        node: str,
        recommendations: list[str],
    ) -> None:
        """Обновить блок результата."""
        self.result_label.setText(f"Диагноз: {diagnosis}")
        self.probability_label.setText(f"Вероятность: {probability}")
        self.node_label.setText(f"Узел: {node}")
        self.recommendations_list.clear()
        for rec in recommendations:
            self.recommendations_list.addItem(rec)


def run_app() -> None:
    """Запустить Qt-приложение."""
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    app.exec()
