"""Demo data used when WhisperX and/or Claude are not configured.

This lets the whole product run end-to-end (upload -> processing -> dashboard)
with zero external dependencies, and doubles as a deterministic fixture for
tests. It mirrors the "Ориент Логистикс" sample call from the design mockups.
"""
from __future__ import annotations

from ..schemas import (
    Analysis,
    CoachingCard,
    CoachingItem,
    EngagementAnalysis,
    EngagementPoint,
    Metrics,
    Moment,
    Turn,
)

MOCK_DURATION = 872.0  # 14:32

MOCK_TURNS: list[Turn] = [
    Turn(speaker="A", speaker_label="Менеджер", start=12, end=44,
         text="Дилшод, спасибо, что нашли время. Прежде чем расскажу про Flaby — расскажите, как сейчас у вас разбирают звонки менеджеров?"),
    Turn(speaker="B", speaker_label="Клиент", start=45, end=95,
         text="Честно — почти никак. Руководитель раз в неделю слушает пару записей вручную. На всё не хватает времени."),
    Turn(speaker="A", speaker_label="Менеджер", start=96, end=121,
         text="То есть основная боль — нет системного контроля качества, и вы не видите, где менеджеры теряют сделки. Правильно понимаю?"),
    Turn(speaker="B", speaker_label="Клиент", start=122, end=155,
         text="Да, именно. И новичков тяжело обучать — нет примеров хороших звонков."),
    Turn(speaker="A", speaker_label="Менеджер", start=240, end=265,
         text="Flaby разбирает каждый звонок за минуты, а не часы: диаризация, график вовлечённости и карточка с тем, что сделано хорошо и что упущено — как раз для обучения новичков."),
    Turn(speaker="B", speaker_label="Клиент", start=340, end=355,
         text="Звучит интересно. Но у нас были неудачные внедрения — команда просто не пользовалась."),
    Turn(speaker="A", speaker_label="Менеджер", start=370, end=510,
         text="Понимаю. Смотрите, у нас всё автоматически: ничего не надо нажимать, интеграция с телефонией сама подтягивает записи, отчёт приходит руководителю в Telegram, есть мобильное приложение, дашборд по команде, экспорт… (продолжает 2 мин 20 сек)"),
    Turn(speaker="B", speaker_label="Клиент", start=514, end=524,
         text="Угу… ладно. А по цене как?"),
    Turn(speaker="A", speaker_label="Менеджер", start=555, end=595,
         text="За 12 менеджеров — 4,2 млн/мес. Но одна возвращённая сделка окупает подписку. Сколько для вас стоит потерянный клиент?"),
    Turn(speaker="B", speaker_label="Клиент", start=620, end=650,
         text="Ну… немало. Средний чек около 30 млн. Надо подумать, обсудить с руководителем."),
    Turn(speaker="A", speaker_label="Менеджер", start=845, end=872,
         text="Хорошо, тогда я пришлю материалы, посмотрите на досуге. Спасибо за разговор!"),
]

MOCK_ENGAGEMENT = EngagementAnalysis(
    score=78,
    score_label="Хороший звонок",
    summary="спад к финалу",
    engagement=[EngagementPoint(t=t, value=v) for t, v in [
        (0, 42), (48, 55), (96, 68), (130, 74), (175, 70), (220, 76), (265, 80),
        (310, 72), (355, 64), (370, 60), (410, 48), (450, 38), (490, 41),
        (510, 47), (555, 63), (600, 71), (650, 66), (700, 58), (750, 52),
        (800, 49), (850, 45), (872, 44),
    ]],
    moments=[
        Moment(t=130, label="Выявление боли", type="good"),
        Moment(t=265, label="Презентация ценности", type="good"),
        Moment(t=370, label="Длинный монолог", type="warn"),
        Moment(t=450, label="Клиент теряет интерес", type="bad"),
        Moment(t=555, label="Отработка возражения", type="good"),
        Moment(t=850, label="Слабый финал", type="warn"),
    ],
    objections_total=2,
    objections_handled=1,
)

MOCK_COACHING = CoachingCard(
    strengths=[
        CoachingItem(title="Выявил боль клиента",
                     detail="открытыми вопросами и резюмировал её словами клиента.",
                     timestamp="01:36 – 02:10"),
        CoachingItem(title="Связал функцию с задачей",
                     detail="«разбор звонков за минуты, а не часы» — говорил ценностью, не фичами.",
                     timestamp="04:00 – 04:25"),
        CoachingItem(title="Отработал возражение по цене",
                     detail="вернув разговор к стоимости упущенных сделок.",
                     timestamp="09:15 – 10:00"),
    ],
    missed=[
        CoachingItem(title="Не зафиксировал бюджет и сроки",
                     detail="решения — квалификация осталась неполной.",
                     timestamp="квалификация"),
        CoachingItem(title="Монолог 2:20 на 06:10",
                     detail="клиент перестал участвовать, вовлечённость упала до 38.",
                     timestamp="06:10 – 08:30"),
        CoachingItem(title="Не назначил следующий шаг",
                     detail="с конкретной датой — звонок завершился размыто.",
                     timestamp="14:00 – 14:32"),
    ],
    next_steps=[
        "Отправить письмо с расчётом ROI и зафиксировать бюджет до пятницы.",
        "Назначить демо с ЛПР по внедрению на след. неделю.",
        "Тренинг: сократить монологи до 45 сек, задавать check-вопрос.",
    ],
)


def mock_engagement() -> EngagementAnalysis:
    return MOCK_ENGAGEMENT.model_copy(deep=True)


def mock_coaching() -> CoachingCard:
    return MOCK_COACHING.model_copy(deep=True)
