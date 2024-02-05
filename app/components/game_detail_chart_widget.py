import darkdetect
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame

from pyecharts.charts import Bar, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
from pyecharts import options as opts

from qfluentwidgets import Theme
from qframelesswindow.webengine import FramelessWebEngineView

from app.common.config import cfg


class GameDetailChartWidget(QFrame):
    loadHtml = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = None
        self.hBoxLayout = QHBoxLayout(self)
        self.browser = FramelessWebEngineView(self.window())
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        self.browser.page().setBackgroundColor(Qt.transparent)
        self.browser.page().settings().setAttribute(
            QWebEngineSettings.ShowScrollBars, False)
        self.browser.setGeometry(0, 0, self.width(), self.height())
        self.setStyleSheet("border: none;")
        self.hBoxLayout.addWidget(self.browser)

        self.loadHtml.connect(self.onLoadHtml)

    def onLoadHtml(self, path):
        self.browser.load(QUrl.fromLocalFile(path))

    def refresh(self):
        self.initChartHtml(self.game)

    def translate(self, orig):
        return {
            'totalDamageDealtToChampions': self.tr('Total Damage dealt to champions'),
            'trueDamageDealtToChampions': self.tr('True damage dealt to champions'),
            'magicDamageDealtToChampions': self.tr('Magic damage dealt to champion'),
            'physicalDamageDealtToChampions': self.tr('Physical damage dealt to champion'),
            'totalDamageTaken': self.tr('Total damage taken'),
            'trueDamageTaken': self.tr('True damage taken'),
            'magicalDamageTaken': self.tr('Magic damage taken'),
            'physicalDamageTaken': self.tr('Physical damage taken'),
            'totalHealingDone': self.tr('Total healing done'),
            'damageSelfMitigated': self.tr('Demage self mitigated'),
            'goldEarned': self.tr('Gold earned'),
            'visionScore': self.tr('Vision score'),
            'totalMinionsKilled': self.tr("Total minions killed"),
        }[orig]

    def initChartHtml(self, game):
        """
        该方法耗时, 不建议在UI线程执行

        执行完成后自动更新到 browser
        """
        self.game = game

        t = cfg.get(cfg.themeMode)

        if t == Theme.AUTO:
            t = darkdetect.theme()

        if t == Theme.DARK:
            chartTheme = ThemeType.DARK
            legendBackgroundcolor = "#FFFFFF11"
        else:
            chartTheme = ThemeType.WHITE
            legendBackgroundcolor = "#00000006"

        bar = Bar(
            init_opts=opts.InitOpts(
                width="100%",
                height="100vh",
                theme=chartTheme,
                bg_color="#00000000",
            )
        )

        keys = ['totalDamageDealtToChampions', 'trueDamageDealtToChampions',
                'magicDamageDealtToChampions', 'physicalDamageDealtToChampions',
                'totalDamageTaken', 'trueDamageTaken', 'magicalDamageTaken',
                'physicalDamageTaken', 'totalHealingDone', 'damageSelfMitigated',
                'totalMinionsKilled', 'goldEarned', 'visionScore']

        summoners = [s for team in game['teams'].values()
                     for s in team['summoners']]

        # 中间加了个假人 ^^
        phantom = {"summonerName": "", 'championIcon': "", 'chartData': {}}
        for k in keys:
            phantom['chartData'][k] = 0

        summoners.insert(5, phantom)

        bar.add_xaxis([s['summonerName'] for s in summoners][::-1])

        # 通过索引判断设置一下颜色
        colorFormatter = """
            function(params) {
                if (params.dataIndex > 5) {
                    return 'blue';
                } else {
                    return 'red';
                }
            }
        """

        for k in keys:
            bar.add_yaxis(
                self.translate(k),
                [s['chartData'][k] for s in summoners][::-1],
                gap="0%",
                itemstyle_opts=opts.ItemStyleOpts(color=JsCode(colorFormatter))
            )

        # 那个假人的数据 "0" 让它不显示
        labelFormatter = """
            function(params) {
                if (params.value === 0) {
                    return '';
                } else {
                    return params.value;
                }
            }
        """

        result = (
            bar
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right",
                                                       formatter=JsCode(labelFormatter)))
            .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                    is_show=False
                ),
                legend_opts=opts.LegendOpts(
                    border_radius=5,
                    selected_map={self.translate(k): False for k in keys[1:]},
                    type_='scroll',
                    background_color=legendBackgroundcolor
                ),
            )
            .render()
        )

        self.loadHtml.emit(result)
