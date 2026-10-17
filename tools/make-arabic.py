#!/usr/bin/env python3
"""Build ar/index.html (Egyptian Arabic, right to left) from index.html.

Run from the repo root after any change to index.html:

    python3 tools/make-arabic.py

Every English string below must still exist in index.html; the script stops
and names any that are missing, so a changed English sentence needs its
Arabic line updated here too.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text(encoding="utf-8")

# (English, Arabic). Longer, more specific strings come before short ones,
# because replacements run in order.
PAIRS = [
    # ---- document head ----
    ('<html lang="en">', '<html lang="ar" dir="rtl">'),
    ('<title>Orbis Solutions</title>', '<title>Orbis | أنظمة إدارة للشركات</title>'),
    ('content="Orbis Software Solution and Technology builds and sells management systems for law offices, clinics, barbershops, shops, warehouses, schools and HR teams."',
     'content="Orbis للحلول البرمجية والتكنولوجيا بتصمم وتبيع أنظمة إدارة لمكاتب المحاماة والعيادات وصالونات الحلاقة والمحلات والمخازن والمدارس وشؤون الموظفين."'),

    # ---- language switch ----
    ('<a class="lang" href="ar/" hreflang="ar" lang="ar" data-lang="ar">عربي</a>',
     '<a class="lang" href="../" hreflang="en" lang="en" data-lang="en">English</a>'),
    ('<a class="plain" href="ar/" hreflang="ar" lang="ar" data-lang="ar">عربي</a>',
     '<a class="plain" href="../" hreflang="en" lang="en" data-lang="en">English</a>'),

    # ---- mega menu: solutions ----
    ('<small>Judicial agenda, cases, powers of attorney</small>', '<small>الأجندة القضائية والقضايا والتوكيلات</small>'),
    ('<small>Dental chart, appointments, billing, profit</small>', '<small>رسم الأسنان والمواعيد والفواتير والأرباح</small>'),
    ('<small>Checkout, invoices and daily sales reports</small>', '<small>البيع والفواتير وتقارير المبيعات اليومية</small>'),
    ('<small>Stock across branches, low-stock alerts</small>', '<small>المخزون في كل الفروع وتنبيهات النواقص</small>'),
    ('<small>Attendance, leave and monthly salaries</small>', '<small>الحضور والإجازات والمرتبات الشهرية</small>'),
    ('<small>Students, classes, fees and grades</small>', '<small>الطلاب والفصول والمصروفات والدرجات</small>'),
    ('Management systems</p>', 'أنظمة الإدارة</p>'),
    ('Featured system', 'نظام مميز'),
    ('Grantira for law offices', 'جرانتيرا لمكاتب المحاماة'),
    ('A judicial agenda drawn like the paper diary, with every hearing, decision and power of attorney.',
     'أجندة قضائية زي الأجندة الورق بالظبط، فيها كل جلسة وقرار وتوكيل.'),

    # ---- mega menu: work ----
    ('Judicial agenda, cases and powers of attorney.', 'الأجندة القضائية والقضايا والتوكيلات.'),
    ('Digital dental chart, billing and profit reports.', 'رسم أسنان رقمي وفواتير وتقارير أرباح.'),
    ('Touch-screen cashier, receipts, stock and profit.', 'كاشير بشاشة لمس وفواتير ومخزن وأرباح.'),
    ('>Explore<', '>استكشف<'),
    ('All projects', 'كل المشاريع'),
    ('How we deliver', 'إزاي بنسلّم'),
    ('Start your project', 'ابدأ مشروعك'),

    # ---- mega menu: company ----
    ('<b>About Orbis</b><small>Who we are and how we think about software</small>', '<b>عن Orbis</b><small>مين إحنا وإزاي بنفكر في البرمجيات</small>'),
    ('<small>Ask for a demo or a quote</small>', '<small>اطلب عرض تجريبي أو عرض سعر</small>'),
    ('Talk to us', 'كلمنا'),
    ('Call or WhatsApp us and we will walk you through a live demo.', 'كلمنا أو ابعتلنا واتساب ونوريك النظام شغال قدامك.'),
    ('Chat on WhatsApp', 'كلمنا واتساب'),

    # ---- mobile menu ----
    ('<small>Cases, clients, court agenda</small>', '<small>القضايا والموكلين والأجندة</small>'),
    ('<small>Patients, appointments, billing</small>', '<small>المرضى والمواعيد والفواتير</small>'),
    ('<small>Checkout and sales reports</small>', '<small>البيع وتقارير المبيعات</small>'),
    ('<small>Stock across branches</small>', '<small>المخزون في كل الفروع</small>'),
    ('<small>Attendance and salaries</small>', '<small>الحضور والمرتبات</small>'),
    ('<small>Students, fees, grades</small>', '<small>الطلاب والمصروفات والدرجات</small>'),
    ('<small>Law office management</small>', '<small>إدارة مكاتب المحاماة</small>'),
    ('<small>Dental clinic management</small>', '<small>إدارة عيادات الأسنان</small>'),
    ('<small>Barbershop and salon management</small>', '<small>إدارة صالونات الحلاقة</small>'),
    ('aria-label="Main"', 'aria-label="القائمة الرئيسية"'),
    ('aria-label="Menu"', 'aria-label="القائمة"'),
    ('aria-label="Open menu"', 'aria-label="فتح القائمة"'),
    ("on ? 'Close menu' : 'Open menu'", "on ? 'إغلاق القائمة' : 'فتح القائمة'"),

    # ---- hero ----
    ('<b>Live</b> Now running in law offices, dental clinics and barbershops', '<b>شغّال</b> شغالين دلوقتي في مكاتب محاماة وعيادات أسنان وصالونات حلاقة'),
    ('<h1>Run your business<br>from <span class="grad">one clear system.</span></h1>',
     '<h1>أدِر شغلك كله<br>من <span class="grad">نظام واحد واضح.</span></h1>'),
    ('Orbis Software Solution and Technology designs, builds and sells management software for law offices, clinics, barbershops, shops, warehouses and schools. Your cases, patients, stock, staff and reports, all in one place.',
     'Orbis للحلول البرمجية والتكنولوجيا بتصمم وتبني وتبيع أنظمة إدارة لمكاتب المحاماة والعيادات وصالونات الحلاقة والمحلات والمخازن والمدارس. قضاياك ومرضاك ومخزونك وموظفينك وتقاريرك، كلها في مكان واحد.'),
    ('alt="Grantira law office dashboard"', 'alt="لوحة جرانتيرا لمكاتب المحاماة"'),
    ('alt="Grantira court agenda"', 'alt="الأجندة القضائية في جرانتيرا"'),
    ('<b>Today at the office</b><small>Hearings, tasks and papers out</small>', '<b>النهارده في المكتب</b><small>الجلسات والمهام والأوراق اللي برّه</small>'),
    ('<b>Court agenda</b><small>Every session by lawyer, with public holidays</small>', '<b>الأجندة القضائية</b><small>كل جلسة حسب المحامي، ومعاها الإجازات الرسمية</small>'),

    # ---- strip ----
    ('One team, systems for many kinds of work', 'فريق واحد وأنظمة لكل أنواع الشغل'),
    ('</svg>Dental clinics</li>', '</svg>عيادات الأسنان</li>'),
    ('</svg>Barbershops</li>', '</svg>صالونات الحلاقة</li>'),
    ('</svg>Retail &amp; POS</li>', '</svg>المحلات ونقاط البيع</li>'),
    ('</svg>Warehouses</li>', '</svg>المخازن</li>'),
    ('</svg>HR teams</li>', '</svg>شؤون الموظفين</li>'),
    ('</svg>Schools</li>', '</svg>المدارس</li>'),

    # ---- our work ----
    ('Systems running in real businesses.', 'أنظمة شغالة في أماكن حقيقية.'),
    ('Three of the systems we have designed, built and delivered. More projects are on the way.', 'تلاتة من الأنظمة اللي صممناها وبنيناها وسلمناها، ومشاريع تانية جاية في الطريق.'),

    # grantira
    ('Windows, Mac, Android, iOS &amp; web', 'ويندوز وماك وأندرويد وiOS والويب'),
    ("Law office management built for firms in Egypt. The paper court diary, the case files and the office's daily follow-up, in one Arabic workspace.",
     'إدارة مكاتب المحاماة، معمولة لمكاتب مصر. الأجندة الورق وملفات القضايا والمتابعة اليومية للمكتب، في مساحة عمل عربية واحدة.'),
    ('<b>Judicial agenda, like the paper diary</b><span>A month calendar with hearings, appointments and official holidays. Each day opens the familiar five-column table: court and case number, client, opponent, previous session, decision. Record a decision with a next date and the next hearing is created automatically.</span>',
     '<b>أجندة قضائية زي الأجندة الورق</b><span>تقويم شهري فيه الجلسات والمواعيد والإجازات الرسمية. كل يوم بيفتح الجدول اللي متعود عليه بخمس أعمدة: المحكمة والدائرة ورقم الدعوى، الموكل، الخصم، الجلسة السابقة، القرار. سجّل القرار بميعاد الجلسة الجاية، والجلسة الجاية تتعمل لوحدها.</span>'),
    ("<b>Today's reminders for every role</b><span>Hearings today and tomorrow, hearings with no decision recorded, tasks due, bailiff papers coming up and open cases with no next hearing. Each one opens its record.</span>",
     '<b>تذكيرات اليوم لكل دور</b><span>جلسات النهارده وبكره، جلسات من غير قرار متسجل، مهام مستحقة، أوراق محضرين قرب ميعادها، وقضايا مفتوحة من غير جلسة جاية. كل تذكير بيفتح على ملفه.</span>'),
    ('<b>Office follow-up for the manager</b><span>One row per person showing what is on them today. Tap a person to see their items and give them a task.</span>',
     '<b>متابعة المكتب للمدير</b><span>صف لكل شخص فيه اللي عليه النهارده. دوس على أي حد تشوف حاجاته وتديله مهمة.</span>'),
    ('<b>Cases, clients and powers of attorney</b><span>Every POA tracked as valid, expiring, expired or revoked, with alerts 30 days ahead and cases without a valid POA flagged.</span>',
     '<b>القضايا والموكلين والتوكيلات</b><span>كل توكيل متابَع: ساري أو قرب ينتهي أو منتهي أو ملغي، مع تنبيه قبلها بـ30 يوم، والقضايا اللي من غير توكيل ساري بتظهر قدامك.</span>'),
    ('<b>Bailiff papers and tasks</b><span>Track every paper with the bailiffs, its session date and whether it was served, and assign tasks to anyone in the office.</span>',
     '<b>أوراق المحضرين والمهام</b><span>تابع كل ورقة مع المحضرين وميعاد جلستها واتعلنت ولا لأ، ووزّع المهام على أي حد في المكتب.</span>'),
    ('<b>Paper and cash custody</b><span>Know who holds each original document, with its full movement history, and what cash each lawyer still holds.</span>',
     '<b>عهدة الأوراق والعهدة النقدية</b><span>اعرف مين ماسك كل ورقة أصل وتاريخ حركتها كله، وكل محامي لسه معاه كام من العهدة.</span>'),
    ('aria-label="Grantira screens"', 'aria-label="شاشات جرانتيرا"'),
    ('"Grantira judicial agenda"', '"الأجندة القضائية في جرانتيرا"'),
    ('>Judicial agenda</button>', '>الأجندة القضائية</button>'),
    ('''"Grantira home with today's reminders">Today's reminders</button>''', '"الرئيسية في جرانتيرا مع تذكيرات اليوم">تذكيرات اليوم</button>'),
    ('"Grantira in light mode">Light mode</button>', '"جرانتيرا في الوضع الفاتح">الوضع الفاتح</button>'),
    ('"Grantira sign-in screen">Sign in</button>', '"شاشة تسجيل الدخول في جرانتيرا">تسجيل الدخول</button>'),
    ('7 roles, from manager to receptionist', '7 أدوار، من المدير لموظف الاستقبال'),
    ('Daily page with Gregorian and Hijri dates', 'صفحة يومية بالتاريخ الميلادي والهجري'),
    ('Shared directory of courts, prosecutions and notaries', 'دليل مشترك للمحاكم والنيابات والشهر العقاري'),
    ('Multiple branches and team accounts', 'فروع متعددة وحسابات للفريق'),
    ('Windows, Mac, Android, iOS and web', 'ويندوز وماك وأندرويد وiOS والويب'),
    ('Full Arabic, with light and dark modes', 'عربي بالكامل، بوضع فاتح وغامق'),
    ('Confidential by design', 'سرية من الأساس'),
    ('Client files stay inside your office.', 'ملفات موكلينك بتفضل جوه مكتبك.'),
    ("<b>Every office fully separated</b><span>Access rules on the server keep each office's data to itself. No other office can see it.</span>",
     '<b>كل مكتب منفصل تمامًا</b><span>قواعد الصلاحيات على السيرفر بتخلي بيانات كل مكتب ليه لوحده، ومفيش مكتب تاني يقدر يشوفها.</span>'),
    ('<b>Lawyers see only their cases</b><span>A lawyer sees a case, its hearings and reminders only when assigned to it. Receptionists and accountants read only.</span>',
     '<b>المحامي يشوف قضاياه بس</b><span>المحامي مايشوفش القضية وجلساتها وتذكيراتها إلا لو متعين عليها. والاستقبال والمحاسب قراءة بس.</span>'),
    ('<b>The manager controls access</b><span>No public sign-up. The manager creates every account, changes roles and can deactivate a user at once.</span>',
     '<b>المدير هو اللي بيتحكم في الدخول</b><span>مفيش تسجيل مفتوح. المدير بيعمل كل الحسابات ويغير الأدوار ويقدر يوقف أي مستخدم في لحظتها.</span>'),

    # clinic
    ('>Arabic &amp; English<', '>عربي وإنجليزي<'),
    ('Windows &amp; Android tablets', 'ويندوز وتابلت أندرويد'),
    ('Dental clinic management from reception to profit report. Everything a clinic runs on, in one system that works the way Egyptian clinics work.',
     'إدارة عيادة الأسنان من الاستقبال لحد تقرير الأرباح. كل اللي العيادة محتاجاه، في نظام واحد ماشي بطريقة شغل العيادات المصرية.'),
    ('<b>Digital dental chart</b><span>Chart every tooth surface (mesial, distal, occlusal, buccal, lingual) with standard FDI numbering. Mark caries, fillings, crowns, root canals, implants and missing teeth.</span>',
     '<b>رسم أسنان رقمي</b><span>سجّل على كل سطح في السنة (Mesial وDistal وOcclusal وBuccal وLingual) بترقيم FDI القياسي. علّم التسوس والحشو والتركيبات وعلاج العصب والزرعات والأسنان المفقودة.</span>'),
    ('<b>The whole visit on one screen</b><span>History, chart, notes, prescriptions, treatment plan and X-rays together, with no jumping between screens.</span>',
     '<b>الزيارة كلها في شاشة واحدة</b><span>التاريخ المرضي ورسم الأسنان والملاحظات والروشتات وخطة العلاج والأشعة مع بعض، من غير تنقل بين الشاشات.</span>'),
    ("<b>Appointments and check-in</b><span>Book by doctor and visit type. Checked-in patients appear on the doctor's waiting list straight away.</span>",
     '<b>المواعيد وتسجيل الحضور</b><span>احجز حسب الدكتور ونوع الزيارة. أول ما الاستقبال يسجل حضور المريض بيظهر في قايمة انتظار الدكتور على طول.</span>'),
    ('<b>Billing the way Egyptians pay</b><span>Cash, Visa, Vodafone Cash, InstaPay and insurance, with partial payments and an unpaid-balance list.</span>',
     '<b>الدفع بالطرق اللي المصريين بيدفعوا بيها</b><span>كاش وفيزا وفودافون كاش وإنستاباي والتأمين، مع الدفع على أجزاء وقايمة بالمبالغ المتبقية.</span>'),
    ('<b>Know your real profit</b><span>Revenue, expenses, profit and cash in hand, with 12-month trends by doctor, treatment or payment method.</span>',
     '<b>اعرف مكسبك الحقيقي</b><span>الإيرادات والمصروفات والربح والكاش اللي في الخزنة، مع اتجاهات 12 شهر حسب الدكتور أو العلاج أو طريقة الدفع.</span>'),
    ('''<b>AI financial assistant</b><span>Ask "Why was this month lower?" in Arabic or English and get answers from your clinic's own numbers.</span>''',
     '<b>مساعد مالي بالذكاء الاصطناعي</b><span>اسأل "ليه الشهر ده كان أقل؟" بالعربي أو الإنجليزي، وخد إجابة من أرقام عيادتك نفسها.</span>'),
    ('aria-label="Orbis Clinic Suite screens"', 'aria-label="شاشات Orbis Clinic Suite"'),
    ('"Dental chart">Dental chart</button>', '"رسم الأسنان">رسم الأسنان</button>'),
    ('alt="Dental chart"', 'alt="رسم الأسنان"'),
    ('"Doctor dashboard">Dashboard</button>', '"لوحة الدكتور">لوحة التحكم</button>'),
    ('"New appointment">Appointments</button>', '"موعد جديد">المواعيد</button>'),
    ('"Invoice with inventory items">Invoices</button>', '"فاتورة بأصناف من المخزن">الفواتير</button>'),
    ('"Dashboard in Arabic">Arabic</button>', '"لوحة التحكم بالعربي">بالعربي</button>'),
    ('5 roles, each with its own dashboard', '5 أدوار، لكل دور لوحة تحكم خاصة بيه'),
    ('Inventory that subtracts supplies automatically', 'مخزن بيخصم الخامات لوحده'),
    ('Full Arabic right-to-left and English', 'عربي كامل من اليمين للشمال وإنجليزي'),
    ('Live sync across Windows PCs and Android tablets', 'مزامنة لحظية بين أجهزة ويندوز وتابلت أندرويد'),
    ('Printed treatment plans and prescriptions', 'طباعة خطط العلاج والروشتات'),
    ('Simple installer, updates without reinstalling', 'تسطيب سهل وتحديثات من غير ما تمسح البرنامج'),
    ('Privacy built in', 'الخصوصية من الأساس'),
    ("Your patients' data stays yours.", 'بيانات مرضاك ملكك إنت.'),
    ("<b>X-rays stay in the clinic</b><span>Images and photos are kept on your clinic's own computer, never in the cloud, and load fast over your local network.</span>",
     '<b>الأشعة بتفضل في العيادة</b><span>الأشعة والصور محفوظة على كمبيوتر عيادتك، عمرها ما بتطلع على الكلاود، وبتفتح بسرعة على شبكة العيادة.</span>'),
    ("<b>Every clinic fully separated</b><span>Each clinic's data is isolated. No other clinic can ever see it.</span>",
     '<b>كل عيادة منفصلة تمامًا</b><span>بيانات كل عيادة معزولة، ومفيش عيادة تانية تقدر تشوفها أبدًا.</span>'),
    ("<b>Permissions enforced by the database</b><span>Not just hidden buttons. A receptionist can't see finances, even with a modified app.</span>",
     '<b>الصلاحيات متطبقة من قاعدة البيانات</b><span>مش مجرد زراير مستخبية. موظف الاستقبال مايقدرش يشوف الحسابات حتى لو معاه نسخة متعدلة من البرنامج.</span>'),

    # barbershop
    ('Windows &amp; touch screens', 'ويندوز وشاشات لمس'),
    ('Barbershop and salon management on one PC at the counter. The cashier, the receipts, the customers, the stock and the money, in a fast Arabic system that works with no internet.',
     'إدارة صالون الحلاقة من كمبيوتر واحد على الكاونتر. الكاشير والفواتير والعملاء والمخزن والفلوس، في نظام عربي سريع شغال من غير إنترنت.'),
    ('<b>A touch-screen cashier</b><span>Tap services and products from big tiles, pick the barber and the customer, give a discount in pounds or percent, then save and print. Cash, Visa or wallet and InstaPay.</span>',
     '<b>كاشير بشاشة لمس</b><span>دوس على الخدمات والمنتجات من مربعات كبيرة، اختار الحلاق والعميل، واعمل خصم بالجنيه أو بالنسبة، وبعدين احفظ واطبع. كاش أو فيزا أو محفظة وإنستاباي.</span>'),
    ("<b>Receipts on a thermal printer</b><span>Your shop's name, phone, address and thank-you message on 58 mm or 80 mm rolls. Reprint any receipt, and only the owner can void one.</span>",
     '<b>فواتير على طابعة حرارية</b><span>اسم المحل وتليفونه وعنوانه ورسالة شكر على رول 58 أو 80 مم. اطبع أي فاتورة تاني، وإلغاء الفاتورة للمالك بس.</span>'),
    ('<b>Customers and their visits</b><span>Type a phone number and the customer comes up with their visit count, total spent and notes like their favourite barber or cut.</span>',
     '<b>العملاء وزياراتهم</b><span>اكتب رقم التليفون والعميل يظهر بعدد زياراته وإجمالي اللي دفعه وملاحظاته، زي الحلاق اللي بيحبه أو طريقة القص.</span>'),
    ('<b>Stock that counts itself</b><span>Products sold at the counter come out of stock on every receipt. Receive goods, record supplies used or damaged, count the shelf, and see what is running low.</span>',
     '<b>مخزن بيحسب نفسه</b><span>المنتجات اللي بتتباع بتتخصم من المخزن مع كل فاتورة. استلم بضاعة، وسجّل المستلزمات المصروفة أو التالفة، واعمل جرد، وشوف إيه اللي قرب يخلص.</span>'),
    ("<b>Staff loans and shop costs</b><span>Record each barber's loans and repayments with the balance left, and the shop's rent, electricity, salaries and other costs by category.</span>",
     '<b>سلف الموظفين ومصروفات المحل</b><span>سجّل سلف كل حلاق والسداد والمتبقي عليه، ومصروفات المحل من إيجار وكهربا ومرتبات وغيرها حسب النوع.</span>'),
    ("<b>The owner's profit report</b><span>Revenue, costs, net profit and cash for any period, with sales per barber, top services and products, and costs by category.</span>",
     '<b>تقرير الأرباح للمالك</b><span>الإيرادات والمصروفات وصافي الربح والنقدية لأي فترة، مع إيراد كل حلاق وأكتر الخدمات والمنتجات مبيعًا والمصروفات حسب النوع.</span>'),
    ('aria-label="Orbis Barbershop screens"', 'aria-label="شاشات Orbis Barbershop"'),
    ('"Cashier screen with a new receipt">Cashier</button>', '"شاشة الكاشير وفاتورة جديدة">الكاشير</button>'),
    ('alt="Cashier screen with a new receipt"', 'alt="شاشة الكاشير وفاتورة جديدة"'),
    ('"Financial reports">Reports</button>', '"التقارير المالية">التقارير</button>'),
    ('"Customers and visit history">Customers</button>', '"العملاء وسجل الزيارات">العملاء</button>'),
    ('"Stock with low-stock status">Stock</button>', '"المخزن وحالة كل صنف">المخزن</button>'),
    ('Owner and cashier roles', 'صلاحيات للمالك والكاشير'),
    ('Fits any screen, down to <span dir="ltr">1024×768</span> touch POS', 'بيظبط على أي شاشة، لحد شاشات الكاشير اللمس <span dir="ltr">1024×768</span>'),
    ('Full Arabic right-to-left, prices in EGP', 'عربي كامل من اليمين للشمال، والأسعار بالجنيه'),
    ('Works offline, no internet needed', 'شغال أوفلاين من غير إنترنت'),
    ('Products for sale and shop supplies', 'منتجات للبيع ومستلزمات للمحل'),
    ('Simple Windows installer', 'تسطيب سهل على ويندوز'),
    ('Your shop, your data', 'محلك وبياناتك'),
    ("Everything stays on the shop's PC.", 'كل حاجة بتفضل على كمبيوتر المحل.'),
    ('<b>Backed up every day</b><span>The system saves a backup automatically each day and keeps the last 30. The owner can also back up to a USB drive and restore it.</span>',
     '<b>نسخة احتياطية كل يوم</b><span>النظام بيحفظ نسخة احتياطية لوحده كل يوم ويحتفظ بآخر 30 نسخة. والمالك كمان يقدر ياخد نسخة على فلاشة ويرجّعها.</span>'),
    ("<b>The cashier sees only the counter</b><span>A cashier makes receipts, adds customers and records costs, but can't change prices, see the profit report, void receipts or delete records.</span>",
     '<b>الكاشير يشوف الكاونتر بس</b><span>الكاشير بيعمل الفواتير ويضيف العملاء ويسجل المصروفات، لكن مايقدرش يغير الأسعار أو يشوف تقرير الأرباح أو يلغي فواتير أو يمسح حاجة.</span>'),
    ('<b>Every login protected</b><span>Each user signs in with their own password, and only the owner adds users or changes their access.</span>',
     '<b>كل دخول محمي</b><span>كل مستخدم بيدخل بكلمة السر بتاعته، والمالك بس هو اللي يضيف مستخدمين أو يغير صلاحياتهم.</span>'),

    # ---- solutions ----
    ('Pick a system, or let us build yours.', 'اختار نظام، أو خلينا نبنيلك نظامك.'),
    ('Start from one of our ready-made systems and adapt it to your business, or ask us for something built from scratch.',
     'ابدأ بنظام من أنظمتنا الجاهزة ونظبطه على شغلك، أو اطلب نظام مبني من الصفر.'),
    ('A judicial agenda like the paper diary, daily reminders, cases, powers of attorney and paper custody.', 'أجندة قضائية زي الورق، وتذكيرات يومية، وقضايا وتوكيلات وعهدة أوراق.'),
    ('Digital dental chart, appointments, billing with Vodafone Cash and InstaPay, and real profit reports.', 'رسم أسنان رقمي ومواعيد ودفع بفودافون كاش وإنستاباي وتقارير أرباح حقيقية.'),
    ('Fast checkout, barcode and receipt printing, customer accounts and daily reports.', 'بيع سريع، وطباعة باركود وإيصالات، وحسابات العملاء وتقارير يومية.'),
    ('Know what you have in every branch, what is running low and when to reorder.', 'اعرف عندك إيه في كل فرع، وإيه اللي قرب يخلص، وإمتى تطلب تاني.'),
    ('Employees, attendance, leave and monthly payroll in one place.', 'الموظفين والحضور والإجازات والمرتبات الشهرية في مكان واحد.'),
    ('Students, classes, fee collection, grades and reports for parents.', 'الطلاب والفصول وتحصيل المصروفات والدرجات وتقارير لأولياء الأمور.'),
    ('class="live">Live<', 'class="live">شغّال<'),

    # ---- process ----
    ('<h3>Understand</h3><p>We learn how your business runs and agree on what the system must do.</p>', '<h3>نفهم شغلك</h3><p>بنفهم شغلك ماشي إزاي ونتفق على اللي النظام لازم يعمله.</p>'),
    ('<h3>Build</h3><p>We set up a ready-made system or build a custom one, and show you progress along the way.</p>', '<h3>نبني</h3><p>بنجهز نظام جاهز أو نبني واحد مخصوص، وبنوريك الشغل أول بأول.</p>'),
    ('<h3>Train &amp; launch</h3><p>We move your data in, train your team and go live together.</p>', '<h3>ندرّب ونشغّل</h3><p>بننقل بياناتك وندرب فريقك ونبدأ التشغيل مع بعض.</p>'),
    ('<h3>Support</h3><p>We stay with you for fixes, updates and new features as you grow.</p>', '<h3>ندعمك</h3><p>بنفضل معاك في الإصلاحات والتحديثات والمميزات الجديدة وإنت بتكبر.</p>'),
    ('From first call to a running system', 'من أول مكالمة لحد ما النظام يشتغل'),

    # ---- about ----
    ('>Who we are<', '>مين إحنا<'),
    ('A software company focused on running businesses better.', 'شركة برمجيات هدفها إن شغلك يمشي أحسن.'),
    ('Orbis builds management systems that replace spreadsheets, notebooks and disconnected apps with one clear tool your team actually uses. We start from how your business works today and shape the system around it.',
     'Orbis بتبني أنظمة إدارة بتحل محل الإكسيل والكشاكيل والبرامج المتفرقة، بأداة واحدة واضحة فريقك هيستخدمها فعلًا. بنبدأ من طريقة شغلك النهارده ونفصّل النظام عليها.'),
    ('Every system we deliver comes with setup, training for your staff and ongoing support.', 'كل نظام بنسلمه معاه تسطيب وتدريب لفريقك ودعم مستمر.'),
    ('<b>Custom</b><span>Built around your workflow</span>', '<b>مخصوص</b><span>متفصّل على طريقة شغلك</span>'),
    ('<b>Ready-made</b><span>Proven systems you can start with fast</span>', '<b>جاهز</b><span>أنظمة مجربة تبدأ بيها بسرعة</span>'),
    ('<b>Bilingual</b><span>Arabic and English interfaces</span>', '<b>بلغتين</b><span>واجهات عربي وإنجليزي</span>'),
    ('<b>Supported</b><span>Training and help after launch</span>', '<b>معاك دايمًا</b><span>تدريب ومساعدة بعد التشغيل</span>'),

    # ---- contact ----
    ("Let's talk about your business.", 'يلا نتكلم عن شغلك.'),
    ('Ask for a demo or a quote. Send the form and it opens a WhatsApp chat with us, with your message ready.', 'اطلب عرض تجريبي أو عرض سعر. ابعت الفورم وهيفتحلك محادثة واتساب معانا والرسالة جاهزة.'),
    ('<dt>Call / WhatsApp</dt>', '<dt>اتصال / واتساب</dt>'),
    ('<dt>Website</dt>', '<dt>الموقع</dt>'),
    ('>Your name<input', '>اسمك<input'),
    ('>Company<input', '>اسم الشركة<input'),
    ('>Your phone<input', '>رقم تليفونك<input'),
    ('>System you need\n', '>النظام اللي محتاجه\n'),
    ('<option>Law Office</option>', '<option>مكتب محاماة</option>'),
    ('<option>Clinic &amp; Dental Center</option>', '<option>عيادة أو مركز أسنان</option>'),
    ('<option>Barbershop &amp; Salon</option>', '<option>صالون حلاقة</option>'),
    ('<option>Sales &amp; Point of Sale</option>', '<option>مبيعات ونقاط بيع</option>'),
    ('<option>Inventory &amp; Warehouse</option>', '<option>مخزون ومخازن</option>'),
    ('<option>School &amp; Training Center</option>', '<option>مدرسة أو مركز تدريب</option>'),
    ('<option>Something custom</option>', '<option>حاجة مخصوصة</option>'),
    ('>Message<textarea', '>رسالتك<textarea'),
    ('placeholder="Tell us a little about your business and what you want to manage."', 'placeholder="احكيلنا شوية عن شغلك وعايز تدير إيه."'),
    ('Send on WhatsApp', 'ابعت على واتساب'),
    ("'Hello Orbis, I would like a demo.\\nName: '", "'أهلًا Orbis، عايز عرض تجريبي.\\nالاسم: '"),
    ("'\\nCompany: '", "'\\nالشركة: '"),
    ("'\\nPhone: '", "'\\nالتليفون: '"),
    ("'\\nSystem: '", "'\\nالنظام: '"),
    ("'Opening WhatsApp. If nothing happens, message us on +20 110 079 5310.'", "'بنفتح واتساب. لو مفتحش، ابعتلنا على \\u200E+20 110 079 5310.'"),

    # ---- footer ----
    ('<p>Software Solution and Technology. Management systems built around how your business works.</p>', '<p>للحلول البرمجية والتكنولوجيا. أنظمة إدارة متفصّلة على طريقة شغلك.</p>'),
    ('<h4>Work</h4>', '<h4>أعمالنا</h4>'),
    ('>Clinics</a>', '>العيادات</a>'),

    # ---- short labels used in many places (keep last) ----
    ('Orbis Software Solution and Technology', 'Orbis للحلول البرمجية والتكنولوجيا'),
    ('Law Offices', 'مكاتب المحاماة'),
    ('Law offices', 'مكاتب المحاماة'),
    ('Clinics &amp; Dental', 'العيادات وطب الأسنان'),
    ('Sales &amp; POS', 'المبيعات ونقاط البيع'),
    ('HR &amp; Payroll', 'شؤون الموظفين والمرتبات'),
    ('Schools &amp; Training', 'المدارس ومراكز التدريب'),
    ('<b>Inventory</b>', '<b>المخازن</b>'),
    ('<h3>Inventory</h3>', '<h3>المخازن</h3>'),
    ('>Inventory</a>', '>المخازن</a>'),
    ('>Legal<', '>قانوني<'),
    ('>Healthcare<', '>رعاية صحية<'),
    ('>Barbershops<', '>صالونات الحلاقة<'),
    ('>Arabic</span>', '>عربي</span>'),
    ('Solutions <svg', 'الحلول <svg'),
    ('>Solutions<', '>الحلول<'),
    ('Our Work <svg', 'أعمالنا <svg'),
    ('>Our work<', '>أعمالنا<'),
    ('Company <svg', 'الشركة <svg'),
    ('>Company<', '>الشركة<'),
    ('How we work', 'طريقة شغلنا'),
    ('>About</a>', '>عن الشركة</a>'),
    ('<b>Contact</b>', '<b>تواصل معنا</b>'),
    ('>Contact<', '>تواصل معنا<'),
    ('See our work', 'شوف أعمالنا'),
    ('Book a demo', 'احجز عرض تجريبي'),
    ('Grantira', 'جرانتيرا'),
    ('<span class="arrow">→</span>', '<span class="arrow">←</span>'),

    # ---- paths: the Arabic page lives one folder down ----
    ('src="assets/', 'src="../assets/'),
    ('href="assets/', 'href="../assets/'),
]

out = src
missing = []
for en, ar in PAIRS:
    if en not in out:
        missing.append(en)
        continue
    out = out.replace(en, ar)

# The redirect to the Arabic page only belongs on the English page.
out, n = re.subn(r"<script>/\* send returning Arabic visitors.*?</script>\n", "", out, flags=re.S)
if n != 1:
    missing.append("<redirect script>")

if missing:
    sys.exit("Not found in index.html (update tools/make-arabic.py):\n  " + "\n  ".join(m[:90] for m in missing))

(ROOT / "ar").mkdir(exist_ok=True)
(ROOT / "ar" / "index.html").write_text(out, encoding="utf-8")
print("Wrote ar/index.html")
