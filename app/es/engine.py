"""Логика экспертной системы.

Формат правил: условия (набор симптомов/флагов) -> диагноз, вероятность, рекомендации.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    """Описывает продукционное правило экспертной системы."""

    conditions: set[str]
    diagnosis: str
    probability: int
    recommendations: list[str]
    node: str


class ExpertSystem:
    """Простейший механизм вывода по правилам ЕСЛИ-ТО."""

    def __init__(self, rules: Iterable[Rule]) -> None:
        self.rules = list(rules)

    def diagnose(self, symptoms: set[str]) -> dict[str, object]:
        """Вернуть наиболее вероятный диагноз на основе совпавших правил."""
        matched = []
        for rule in self.rules:
            # Если все условия правила входят в набор симптомов — правило сработало.
            if rule.conditions.issubset(symptoms):
                matched.append(rule)

        if not matched:
            return {
                "diagnosis": "Недостаточно данных для точного диагноза",
                "probability": 40,
                "recommendations": [
                    "Уточните симптомы и повторите диагностику.",
                    "Проверьте коды ошибок через OBD-II.",
                ],
                "node": "Не определено",
            }

        # Выбираем правило с максимальной вероятностью.
        best_rule = max(matched, key=lambda rule: rule.probability)
        return {
            "diagnosis": best_rule.diagnosis,
            "probability": best_rule.probability,
            "recommendations": best_rule.recommendations,
            "node": best_rule.node,
        }


def load_default_rules() -> list[Rule]:
    """Набор стартовых правил для учебного проекта."""
    return [
        Rule(
            conditions={
                "Не заводится (стартер не крутит)",
                "Аккумулятор",
            },
            diagnosis="Разряжен аккумулятор или плохой контакт клемм",
            probability=85,
            recommendations=[
                "Проверьте заряд аккумулятора мультиметром.",
                "Очистите клеммы и убедитесь в надежности соединений.",
                "При необходимости зарядите или замените аккумулятор.",
            ],
            node="Электрооборудование",
        ),
        Rule(
            conditions={
                "Не заводится (стартер крутит)",
                "Check Engine",
                "Потеря мощности",
            },
            diagnosis="Проблемы с системой подачи топлива",
            probability=78,
            recommendations=[
                "Проверьте давление топлива и работу бензонасоса.",
                "Осмотрите топливный фильтр на загрязнение.",
                "Снимите показания ошибок через OBD-II.",
            ],
            node="Двигатель",
        ),
        Rule(
            conditions={
                "Троит",
                "Повышенный расход топлива",
                "Check Engine",
            },
            diagnosis="Неисправность системы зажигания (свечи/катушки)",
            probability=82,
            recommendations=[
                "Проверьте свечи зажигания и зазоры.",
                "Диагностируйте катушки зажигания.",
                "После замены сбросьте ошибки ЭБУ.",
            ],
            node="Двигатель",
        ),
        Rule(
            conditions={
                "Стук на кочках",
                "Уводит в сторону",
            },
            diagnosis="Износ элементов подвески или рулевого управления",
            probability=75,
            recommendations=[
                "Проверьте шаровые опоры и сайлентблоки.",
                "Осмотрите рулевые тяги и наконечники.",
                "Сделайте развал-схождение.",
            ],
            node="Ходовая",
        ),
        Rule(
            conditions={
                "Скрип при торможении",
                "Увеличенный ход педали",
            },
            diagnosis="Износ тормозных колодок или утечка жидкости",
            probability=80,
            recommendations=[
                "Осмотрите состояние колодок и дисков.",
                "Проверьте уровень тормозной жидкости.",
                "При необходимости прокачайте систему.",
            ],
            node="Тормозная система",
        ),
        Rule(
            conditions={
                "Подтёки антифриза",
                "Температура ОЖ",
            },
            diagnosis="Утечка охлаждающей жидкости",
            probability=88,
            recommendations=[
                "Осмотрите патрубки и радиатор на утечки.",
                "Проверьте крышку расширительного бачка.",
                "Долейте антифриз до нормы и устраните течь.",
            ],
            node="Система охлаждения",
        ),
        Rule(
            conditions={
                "Вибрация на скорости",
                "На высоких оборотах",
            },
            diagnosis="Дисбаланс колес или износ шин",
            probability=70,
            recommendations=[
                "Проверьте давление в шинах.",
                "Сделайте балансировку колес.",
                "Осмотрите шины на износ и повреждения.",
            ],
            node="Ходовая",
        ),
        Rule(
            conditions={
                "Быстро разряжается аккумулятор",
                "На прогретом двигателе",
            },
            diagnosis="Неисправен генератор или регулятор напряжения",
            probability=76,
            recommendations=[
                "Проверьте напряжение зарядки (13.8–14.5 В).",
                "Осмотрите ремень генератора.",
                "При необходимости замените регулятор или генератор.",
            ],
            node="Электрооборудование",
        ),
    ]
