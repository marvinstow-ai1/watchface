import ui from '@zos/ui'

const N = ui.show_level.ONLY_NORMAL
const arr = (dir) => [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => `${dir}/${n}.png`)
const TIME = arr('time')
const DATE = arr('date')
const SMALL = arr('small')
const WEEK = [1, 2, 3, 4, 5, 6, 7].map((n) => `week/${n}.png`)
const BATT = [0, 1, 2, 3, 4, 5].map((n) => `batt/${n}.png`)

WatchFace({
  build() {
    ui.createWidget(ui.widget.IMG, { x: 0, y: 0, src: 'bg.png', show_level: N })

    // Uhrzeit oben links (24h)
    ui.createWidget(ui.widget.IMG_TIME, {
      hour_zero: 1, hour_startX: 30, hour_startY: 4, hour_array: TIME, hour_space: 0,
      hour_unit_en: 'time/colon.png', hour_unit_sc: 'time/colon.png', hour_unit_tc: 'time/colon.png',
      hour_align: ui.align.LEFT,
      minute_zero: 1, minute_follow: 1, minute_array: TIME, minute_space: 0,
      show_level: N,
    })

    // Wochentag (deutsch) über der unteren HP-Leiste
    ui.createWidget(ui.widget.IMG_WEEK, {
      x: 158, y: 250, week_en: WEEK, week_sc: WEEK, week_tc: WEEK, show_level: N,
    })

    // Datum TT.MM unter der HP-Leiste
    ui.createWidget(ui.widget.IMG_DATE, {
      day_startX: 232, day_startY: 298, day_zero: 1, day_space: 0, day_align: ui.align.LEFT,
      day_en_array: DATE, day_sc_array: DATE, day_tc_array: DATE,
      day_unit_en: 'date/dot.png', day_unit_sc: 'date/dot.png', day_unit_tc: 'date/dot.png',
      show_level: N,
    })
    ui.createWidget(ui.widget.IMG_DATE, {
      month_startX: 289, month_startY: 298, month_zero: 1, month_space: 0, month_align: ui.align.LEFT,
      month_en_array: DATE, month_sc_array: DATE, month_tc_array: DATE,
      show_level: N,
    })

    // Schritte unten links
    ui.createWidget(ui.widget.IMG, { x: 12, y: 366, src: 'shoe.png', show_level: N })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: 36, y: 365, w: 122, h: 18, font_array: SMALL, h_space: 0,
      align_h: ui.align.LEFT, type: ui.data_type.STEP, show_level: N,
    })

    // Akku unten links
    ui.createWidget(ui.widget.IMG_LEVEL, {
      x: 14, y: 408, image_array: BATT, image_length: 6, type: ui.data_type.BATTERY, show_level: N,
    })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: 36, y: 405, w: 120, h: 18, font_array: SMALL, h_space: 0,
      unit_en: 'small/pct.png', unit_sc: 'small/pct.png', unit_tc: 'small/pct.png',
      align_h: ui.align.LEFT, type: ui.data_type.BATTERY, show_level: N,
    })
  },
  onInit() {},
  onDestroy() {},
})
