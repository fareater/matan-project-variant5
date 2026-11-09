from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from PIL import Image
import numpy as np

PUR = RGBColor(0x96, 0x00, 0xFF); PINK = RGBColor(0xE0, 0x30, 0x9A); DARK = RGBColor(0x1E, 0x1E, 0x1E)
GRAY = RGBColor(0x5A, 0x5A, 0x5A); LIGHT = RGBColor(0xF3, 0xEA, 0xFF); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEAL = RGBColor(0x00, 0x8C, 0x8C)
FONT = 'Arial'

prs = Presentation('base.pptx')
S = list(prs.slides)

def drop(shape):
    shape._element.getparent().remove(shape._element)

def clean(slide, keep_title=True):
    for sh in list(slide.shapes):
        if sh.is_placeholder and sh.placeholder_format.type is not None and 'TITLE' in str(sh.placeholder_format.type) and keep_title:
            continue
        if sh.shape_type == 13:  # picture (background art on last slide)
            continue
        drop(sh)

def title(slide, text, color=None):
    for sh in slide.shapes:
        if sh.is_placeholder and 'TITLE' in str(sh.placeholder_format.type):
            sh.width = Inches(7.6)
            tf = sh.text_frame; tf.text = text
            r = tf.paragraphs[0].runs[0]
            r.font.size = Pt(24)
            if color is not None: r.font.color.rgb = color
            return sh

def tb(slide, x, y, w, h, paras, size=14, color=DARK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.05, space=4):
    """paras: str | list[str | list[(text, opts)]]"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
        setattr(tf, side, Inches(margin))
    if isinstance(paras, str): paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.space_after = Pt(space)
        runs = p if isinstance(p, list) else [(p, {})]
        for text, o in runs:
            r = para.add_run(); r.text = text
            f = r.font; f.name = FONT; f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold)
            f.italic = o.get('italic', False); f.color.rgb = o.get('color', color)
    return box

def card(slide, x, y, w, h, fill=LIGHT, line=None, radius=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = radius
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb = line; shp.line.width = Pt(1)
    shp.shadow.inherit = False
    return shp

def circle(slide, x, y, d, text, fill=PUR, size=14):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    return c

def img(slide, path, x, y, w=None, h=None):
    W, H = Image.open(path).size
    if w and not h: h = w * H / W
    if h and not w: w = h * W / H
    return slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))

def img_fit(slide, path, x, y, w, h):
    W, H = Image.open(path).size
    if w / h > W / H:
        nw = h * W / H; return img(slide, path, x + (w - nw) / 2, y, h=h)
    nh = w * H / W; return img(slide, path, x, y + (h - nh) / 2, w=w)

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

# content area inside light frame
X0, Y0, X1, Y1 = 0.55, 1.42, 8.85, 5.12
CW = X1 - X0

# ================= 1. Титул
s = S[0]; clean(s, keep_title=False)
tb(s, 1.0, 2.05, 8.0, 1.0, [[('Оценка стоимости информационных атак и защиты', {'bold': True})]], size=28, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, 1.0, 3.05, 8.0, 0.75, 'Кратные интегралы и метод Лагранжа для выбора оптимального уровня затрат на защиту', size=15, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, 1.0, 4.05, 8.0, 0.8, ['Вариант 5 · Математический анализ, 3 семестр · Информационная безопасность',
                            'Команда: [ФИО] — математик · [ФИО] — вычислитель',
                            '[ФИО] — визуализатор · [ФИО] — ИБ-интерпретатор'],
   size=12, color=WHITE, align=PP_ALIGN.CENTER, space=2)
notes(s, 'Здравствуйте! Наша команда решала задачу варианта 5: как с помощью кратных интегралов найти оптимальный уровень затрат на защиту информационной системы. Заказчик — CISO и финансовый директор организации.')

# ================= 2. Контекст (фиолетовый слайд)
s = S[1]; clean(s); title(s, 'Контекст и вопрос заказчика', color=WHITE)
tb(s, 0.85, 1.35, 4.3, 0.4, [[('Ситуация', {'bold': True, 'color': PUR})]], size=16)
tb(s, 0.85, 1.8, 4.3, 3.0, [
    [('ИС стоит ', {}), ('V = 10 млн ₽', {'bold': True}), (', бюджет на защиту ограничен.', {})],
    [('Успех атаки зависит от ', {}), ('затрат на защиту', {'bold': True}), (' и ', {}), ('квалификации', {'bold': True}), (' злоумышленника q.', {})],
    [('Ущерб растёт с ', {}), ('временем', {'bold': True}), (' t, пока взлом не обнаружен.', {})],
    [('Деньги можно вложить в ', {}), ('предотвращение', {'bold': True}), (' (x₁) или ', {}), ('обнаружение', {'bold': True}), (' (x₂).', {})],
], size=14, space=8)
card(s, 5.45, 1.4, 3.35, 1.75, fill=LIGHT)
tb(s, 5.6, 1.5, 3.1, 1.6, [[('«Сколько тратить на защиту и куда — чтобы убытки плюс затраты были минимальны?»', {'italic': True, 'bold': True, 'color': PUR})]], size=15, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 5.45, 3.3, 3.4, 1.6, [[('Что даём: ', {'bold': True}), ('функцию ожидаемых убытков как двойной интеграл, оптимальный бюджет B* и его разбиение x₁ / x₂, границы применимости.', {})]], size=13)
notes(s, 'Организация защищает систему стоимостью 10 миллионов. Вероятность успешной атаки зависит от затрат на защиту и квалификации злоумышленника, а убыток — от того, сколько времени система взломана. Заказчик спрашивает: сколько тратить и куда — в предотвращение или в обнаружение.')

# ================= 3. Модель
s = S[2]; clean(s); title(s, 'Модель: четыре кирпичика и один интеграл')
comps = [('f_P', 'Вероятность успешной атаки', 'падает с затратами x₁; против q = 1 защита бессильна'),
         ('f_T', 'Окно до обнаружения', 't ~ U[0, T]; мониторинг x₂ сужает окно (T₀ = 90 дн.)'),
         ('f_L', 'Убыток от времени', 'растёт и насыщается на стоимости ИС V'),
         ('f_f', 'Квалификация атакующего', 'q ~ Beta(2,2): много «средних», мало новичков и APT')]
cw = (CW - 0.3 * 3) / 4
for i, (f, h, d) in enumerate(comps):
    x = X0 + i * (cw + 0.3)
    card(s, x, Y0, cw, 1.75)
    img_fit(s, f'figs/{f}.png', x + 0.1, Y0 + 0.1, cw - 0.2, 0.42)
    tb(s, x + 0.1, Y0 + 0.55, cw - 0.2, 0.45, [[(h, {'bold': True, 'color': PUR})]], size=12)
    tb(s, x + 0.1, Y0 + 1.0, cw - 0.2, 0.75, d, size=11, color=GRAY)
tb(s, X0, 3.42, 2.0, 0.4, [[('Ожидаемые убытки', {'bold': True})]], size=14)
img_fit(s, 'figs/f_E.png', X0 + 2.0, 3.3, 6.0, 0.65)
tb(s, X0, 4.38, 2.0, 0.4, [[('Цель', {'bold': True})]], size=14)
img_fit(s, 'figs/f_C.png', X0 + 2.0, 4.3, 3.9, 0.5)
tb(s, X0 + 6.2, 4.15, 2.65, 0.8, ['Параметры: a = b = 1,2 1/млн ₽;', 'g = 0,04 1/день; V = 10 млн ₽'], size=11, color=GRAY, space=1)
notes(s, 'Модель собрана из четырёх функций. Вероятность успеха экспоненциально падает с затратами на предотвращение, но против идеального злоумышленника не помогает. Мониторинг сокращает окно до обнаружения. Убыток растёт со временем и насыщается на стоимости системы. Квалификация распределена по бета-закону. Ожидаемые убытки — двойной интеграл по квалификации и времени с переменной верхней границей T(x2). Минимизируем сумму затрат и убытков.')

# ================= 4. Как считаем интеграл
s = S[3]; clean(s); title(s, 'Как считаем двойной интеграл и насколько ему верить')
circle(s, X0, Y0 + 0.05, 0.42, '1')
tb(s, X0 + 0.55, Y0, 3.6, 0.5, [[('Внутренний по t — аналитически (sympy)', {'bold': True})]], size=14)
img_fit(s, 'figs/f_inner.png', X0 + 0.55, Y0 + 0.5, 3.6, 0.6)
circle(s, X0, Y0 + 1.35, 0.42, '2')
tb(s, X0 + 0.55, Y0 + 1.3, 3.6, 1.0, [[('Внешний по q — scipy.quad', {'bold': True})], 'одномерный, быстрый — можно вызывать тысячи раз в оптимизации'], size=14)
circle(s, X0, Y0 + 2.5, 0.42, '3')
tb(s, X0 + 0.55, Y0 + 2.45, 3.6, 1.2, [[('Проверка двумя независимыми путями', {'bold': True})], 'dblquad по исходному интегралу и Монте-Карло по синтетическому CSV (20 000 атак)'], size=14)
rows = [('Точка (x₁; x₂)', 'quad ∘ sympy', 'dblquad', 'Монте-Карло'),
        ('(0; 0)', '5,0454', '5,0454', '5,06 ± 0,04'),
        ('(1; 0,5)', '2,3542', '2,3542', '2,36 ± 0,02'),
        ('(0,99; 0,64)', '2,2189', '2,2189', '2,22 ± 0,02')]
tx = X0 + 4.4; tw = CW - 4.4
t = s.shapes.add_table(4, 4, Inches(tx), Inches(Y0 + 0.05), Inches(tw), Inches(1.9)).table
cws = [1.25, 1.05, 0.9, tw - 3.2]
for j, wv in enumerate(cws): t.columns[j].width = Inches(wv)
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        c = t.cell(i, j); c.text = v
        p = c.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER if j else PP_ALIGN.LEFT
        r = p.runs[0]; r.font.size = Pt(12); r.font.name = FONT; r.font.bold = (i == 0)
        r.font.color.rgb = WHITE if i == 0 else DARK
        c.fill.solid(); c.fill.fore_color.rgb = PUR if i == 0 else (LIGHT if i % 2 else WHITE)
tb(s, tx, Y0 + 2.2, tw, 1.5, [[('Погрешность: ', {'bold': True}), ('оценка scipy < 10⁻¹³; Монте-Карло совпадает в пределах 95 %-ного интервала. ', {}),
                                ('Ошибка модели (допущения) на порядки больше вычислительной — ей посвящены последние слайды.', {'color': PUR})]], size=13)
notes(s, 'Внутренний интеграл по времени берём аналитически в sympy, внешний по квалификации — численно через quad. Это проверяем двумя независимыми способами: dblquad по исходному двойному интегралу и Монте-Карло по синтетическому набору из 20 тысяч атак. Совпадение до четвёртого знака, оценка погрешности scipy меньше 10 в минус 13-й. Важно: вычислительная погрешность ничтожна, главная неопределённость — в допущениях модели.')

# ================= 5. Лагранж
s = S[4]; clean(s); title(s, 'Метод Лагранжа: сколько стоит последний рубль защиты')
img_fit(s, 'figs/f_lag.png', X0, Y0 - 0.05, 3.6, 0.45)
img_fit(s, 'figs/f_lag2.png', X0 + 4.2, Y0 - 0.05, 4.2, 0.45)
img_fit(s, 'figs/lambda.png', X0, Y0 + 0.5, CW, Y1 - Y0 - 0.55)
notes(s, 'Для каждого бюджета B решаем задачу условной оптимизации: минимум ожидаемых убытков при x1 + x2 = B. Условие Лагранжа: частные производные по x1 и x2 равны минус лямбда. Лямбда — это сколько миллионов убытков спасает последний миллион защиты. Пока лямбда больше единицы, вкладывать выгодно. Оптимальный бюджет — там, где лямбда равна единице: B* = 1,63 млн. Производную по x2 берём по правилу Лейбница, потому что x2 стоит в пределе интегрирования.')

# ================= 6. Результат
s = S[5]; clean(s); title(s, 'Результат: 1,63 млн ₽ на защиту снижают потери на 24 %')
stats = [('1,63 млн ₽', 'оптимальный бюджет B*', PUR), ('0,99 / 0,64', 'x₁ предотвр. / x₂ обнаруж., млн ₽', DARK), ('−1,20 млн ₽', 'общих потерь в год vs «без защиты»', PINK)]
for i, (v, l, col) in enumerate(stats):
    y = Y0 + i * 1.23
    card(s, X0, y, 3.4, 1.05)
    tb(s, X0 + 0.15, y + 0.05, 3.1, 0.6, [[(v, {'bold': True, 'color': col})]], size=26)
    tb(s, X0 + 0.15, y + 0.62, 3.1, 0.45, l, size=12, color=GRAY)
cd = CategoryChartData()
cd.categories = ['Без защиты', 'Только мониторинг', 'Только предотвр.', 'Оптимум']
cd.add_series('Затраты на защиту', (0, 1.265, 1.625, 1.626))
cd.add_series('Ожидаемые убытки', (5.045, 2.753, 2.332, 2.220))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, Inches(X0 + 3.7), Inches(Y0), Inches(CW - 3.9), Inches(Y1 - Y0 - 0.05), cd)
ch = gf.chart
ch.has_title = True; ch.chart_title.text_frame.text = 'Общие потери C = затраты + убытки, млн ₽'
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(13)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.has_legend = True; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(11)
from pptx.enum.chart import XL_LEGEND_POSITION
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
for ser, col in zip(ch.plots[0].series, [DARK, PUR]):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col
ch.plots[0].gap_width = 60
pl = ch.plots[0]; pl.has_data_labels = True
pl.data_labels.number_format = '0.00;;;'; pl.data_labels.number_format_is_linked = False
pl.data_labels.font.size = Pt(11); pl.data_labels.font.color.rgb = WHITE; pl.data_labels.position = XL_LABEL_POSITION.CENTER
ch.category_axis.tick_labels.font.size = Pt(11)
va = ch.value_axis; va.tick_labels.font.size = Pt(10); va.maximum_scale = 5.5; va.minimum_scale = 0; va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = RGBColor(0xE6, 0xE6, 0xE6)
notes(s, 'Итог: оптимально тратить 1,63 млн в год — примерно 1 млн на предотвращение и 0,64 на обнаружение. Общие потери падают с 5,05 до 3,85 млн, то есть на 24 процента. Обе «однобокие» стратегии хуже: только предотвращение — 3,96, только мониторинг — 4,02. Смешанная стратегия выигрывает, потому что меры работают против разных частей риска.')

# ================= 7. 3D
s = S[6]; clean(s); title(s, '3D: поверхность общих потерь — чаша с широким дном')
img_fit(s, 'figs/surface3d.png', X0, Y0 - 0.05, CW, 3.3)
tb(s, X0, Y1 - 0.38, CW, 0.4, [[('Дно пологое: ', {'bold': True}), ('при сдвиге на ±0,3 млн от оптимума потери растут меньше чем на 0,05 млн — важен порядок суммы, а не точная цифра.', {})]], size=13)
notes(s, 'Слева — поверхность общих потерь, справа — её линии уровня. Видно, что функция выпуклая, оптимум единственный. Дно чаши пологое: если ошибиться на 300 тысяч в любую сторону, потери вырастут меньше чем на 50 тысяч. Для заказчика это значит: важно попасть в правильный порядок бюджета, а не в точную цифру.')

# ================= 8. Интерактив
s = S[7]; clean(s); title(s, 'Интерактив: кто атакует — меняет, куда тратить')
img_fit(s, 'figs/slider.png', X0, Y0 - 0.05, CW, 2.65)
card(s, X0, Y0 + 2.7, CW, 0.95)
tb(s, X0 + 0.15, Y0 + 2.75, CW - 0.3, 0.85, [[('Слайдер q̄ (средняя квалификация) в ноутбуке: ', {'bold': True, 'color': PUR}),
    ('против слабых злоумышленников выгодно предотвращение, против сильных — обнаружение. Кривая C(B), E(B) и разбиение x₁/x₂ перестраиваются вживую (interactive_budget.html).', {})]], size=13, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'Здесь в видео показываем 30 секунд интерактива: двигаем слайдер средней квалификации злоумышленника. При q-среднем 0,3 почти весь бюджет идёт в предотвращение. При 0,7 — наоборот, в мониторинг: сильного злоумышленника не остановить на входе, но можно быстрее найти. Это главный практический вывод для CISO: модель угроз определяет структуру бюджета.')

# ================= 9. Границы применимости
s = S[8]; clean(s); title(s, 'Границы применимости: где оптимум «уходит в угол»')
img_fit(s, 'figs/bounds.png', X0, Y0 - 0.05, CW, 3.0)
tb(s, X0, Y0 + 3.0, CW / 2 - 0.15, 0.7, [[('q̄ ≳ 0,72 (APT): ', {'bold': True, 'color': PINK}), ('модель советует x₁ = 0 — не значит «гигиена не нужна», значит exp-модель P здесь неприменима.', {})]], size=12)
tb(s, X0 + CW / 2 + 0.15, Y0 + 3.0, CW / 2 - 0.15, 0.7, [[('g вне [0,022; 0,060]: ', {'bold': True, 'color': PINK}), ('при медленном ущербе — только мониторинг, при быстром (шифровальщик) — только предотвращение.', {})]], size=12)
notes(s, 'Ищем, где метод перестаёт давать содержательный ответ. Слева: при средней квалификации выше 0,72 оптимальные вложения в предотвращение обнуляются. Это не рекомендация отказаться от базовой защиты, а сигнал, что экспоненциальная модель вероятности тут неприменима. Справа: по скорости ущерба g есть два порога. Ниже 0,022 выгоден только мониторинг, выше 0,06 — только предотвращение: при быстром ущербе обнаружение просто опаздывает.')

# ================= 10. Шум
s = S[9]; clean(s); title(s, 'Устойчивость к шуму: решение «гуляет», потери — нет')
img_fit(s, 'figs/noise.png', X0, Y0 - 0.05, CW, 2.85)
tb(s, X0, Y0 + 2.9, CW, 0.8, [[('300 прогонов: ', {'bold': True}), ('a, b, g ± 10 %, стоимость защиты ± 20 %. B* лежит в [1,02; 2,26] млн, но если всё равно применить номинальное решение, медианная потеря — всего 0,04 млн (≈1 % от C*), 95 % — до 0,19 млн.', {})]], size=13)
notes(s, 'Зашумляем ключевые параметры на 10 процентов, а стоимость защиты — на 20, по требованиям методички, и повторяем оптимизацию 300 раз. Оптимальный бюджет заметно плавает — от 1 до 2,3 млн. Но если применять наше номинальное решение, мы теряем в медиане всего 40 тысяч, около процента. Значит, решение устойчиво по потерям, хотя сама цифра B* чувствительна.')

# ================= 11. Границы модели
s = S[10]; clean(s); title(s, 'Границы модели: что результат НЕ означает')
lims = [('Модель', 'q и t независимы, одна атака в год. Сильный злоумышленник дольше прячется — учёт этой связи сдвинет бюджет к мониторингу.'),
        ('Данные', 'a, b, g не измеряются напрямую. Шум 10–20 % двигает B* в 2 раза; доверять стоит порядку суммы, а не цифре.'),
        ('Интерпретация', 'C* = 3,85 млн — среднее по ансамблю атак, а не прогноз на год. Хвост (катастрофа), штрафы и репутация не учтены.'),
        ('Практика', 'Затраты непрерывны, а защиту покупают «пакетами» (SIEM, штат SOC). Обнаружение нужно и для расследования — в L(q,t) этого нет.')]
gw = (CW - 0.3) / 2; gh = 1.62
for i, (h, d) in enumerate(lims):
    x = X0 + (i % 2) * (gw + 0.3); y = Y0 + (i // 2) * (gh + 0.2)
    card(s, x, y, gw, gh)
    circle(s, x + 0.15, y + 0.15, 0.4, str(i + 1), fill=PINK if i == 2 else PUR)
    tb(s, x + 0.65, y + 0.15, gw - 0.8, 0.4, [[(h, {'bold': True})]], size=15, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + 0.15, y + 0.65, gw - 0.3, gh - 0.7, d, size=12, color=GRAY)
notes(s, 'Четыре конкретных ограничения. Модель: считаем квалификацию и время независимыми, хотя сильный злоумышленник обычно ещё и дольше остаётся незамеченным. Данные: параметры эффективности не измеряются напрямую, шум сильно сдвигает B*. Интерпретация: 3,85 млн — это среднее, а не прогноз; модель не говорит о худшем сценарии. Практика: защита покупается дискретно, а мониторинг полезен и для расследования, чего в модели нет.')

# ================= 12. Выводы
s = S[11]; clean(s); title(s, 'Выводы')
outs = [('Двойной интеграл', 'превращает «вероятность × убыток» в функцию затрат E(x₁, x₂), которую можно дифференцировать и оптимизировать.'),
        ('λ(B*) = 1', 'оптимальный бюджет — где последний рубль защиты спасает ровно рубль убытков: B* ≈ 1,63 млн ₽ (16 % стоимости ИС).'),
        ('Смешанная стратегия', 'выигрывает у «однобоких»: потери 3,85 против 3,96–4,02 и 5,05 млн без защиты.'),
        ('Модель угроз решает', 'структура бюджета зависит от q̄ и скорости ущерба g сильнее, чем от точных значений параметров.')]
for i, (h, d) in enumerate(outs):
    y = Y0 + i * 0.92
    circle(s, X0, y + 0.08, 0.5, str(i + 1), fill=PUR, size=16)
    tb(s, X0 + 0.7, y, CW - 1.0, 0.9, [[(h + ' — ', {'bold': True, 'color': PUR}), (d, {})]], size=14, anchor=MSO_ANCHOR.MIDDLE)
notes(s, 'Итого: двойной интеграл даёт функцию ожидаемых убытков, метод Лагранжа — правило «вкладывать, пока рубль защиты спасает больше рубля», оптимум 1,63 млн. Смешанная стратегия лучше однобоких. И главное для заказчика: структура бюджета определяется моделью угроз. Спасибо, готовы ответить на вопросы.')

# ================= 13. Технический минимум
s = S[12]; clean(s); title(s, 'Приложение: технический минимум (у каждого участника)')
rows = [('№', 'Задание', 'Результат', 'Что значит для ИБ'),
        ('1', '∂R/∂q для R = P·L = exp(−a x₁(1−q)) · V(1 − exp(−gqt))', 'V·exp(−a x₁(1−q)) · [a x₁(1 − exp(−gqt)) + g t·exp(−gqt)]', 'квалификация бьёт дважды: пробивает защиту и быстрее наносит ущерб'),
        ('2', '∇R в точке (1; 0,5; 30)', '(−1,49; 6,59; 0,060)', 'самая чувствительная координата — q: «кто атакует» важнее «сколько внутри»'),
        ('3', 'Лагранж: 4·exp(−1,2x₁) + 3·exp(−x₂) → min при x₁ + x₂ = 2', 'x₁ = 1,123; x₂ = 0,877; λ = 1,248', 'λ > 1 — бюджет стоит увеличить'),
        ('4', '∬_D 6q(1−q) · Vqt / T² dt dq,  D = [0,1]×[0,90]', '2,5 млн ₽', 'без защиты теряем ≈ 25 % стоимости ИС'),
        ('5', 'scipy: minimize и dblquad', 'совпадает (± 5·10⁻¹⁴)', 'ручной счёт подтверждён численно')]
t = s.shapes.add_table(6, 4, Inches(X0), Inches(Y0), Inches(CW), Inches(3.0)).table
for j, wv in enumerate([0.4, 2.7, 2.5, CW - 5.6]): t.columns[j].width = Inches(wv)
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        c = t.cell(i, j); c.text = v
        c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.03)
        r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(12); r.font.name = FONT; r.font.bold = (i == 0)
        r.font.color.rgb = WHITE if i == 0 else DARK
        c.fill.solid(); c.fill.fore_color.rgb = PUR if i == 0 else (LIGHT if i % 2 else WHITE)
notes(s, 'Приложение: пять заданий технического минимума с ручным расчётом, проверкой в sympy и scipy и интерпретацией для ИБ. Фото рукописей — в ноутбуке, раздел 1.')

# ================= 14. Спасибо
s = S[13]; clean(s, keep_title=False)

prs.save('Проект_Вариант5_презентация.pptx')
print('saved')
