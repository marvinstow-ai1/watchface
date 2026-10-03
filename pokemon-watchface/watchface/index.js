import ui from '@zos/ui'

const N = ui.show_level.ONLY_NORMAL

// Design (390x450) verkleinert und mittig, damit die runden Ecken nichts abschneiden.
// SCALE muss zu tools/inset_layout.py passen (die Assets sind bereits verkleinert).
const SCALE = 0.86
const OX = Math.floor((390 - Math.round(390 * SCALE)) / 2)
const OY = Math.floor((450 - Math.round(450 * SCALE)) / 2)
const X = (x) => OX + Math.round(x * SCALE)
const Y = (y) => OY + Math.round(y * SCALE)
const L = (v) => Math.round(v * SCALE)
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
      hour_zero: 1, hour_startX: X(30), hour_startY: Y(4), hour_array: TIME, hour_space: 0,
      hour_unit_en: 'time/colon.png', hour_unit_sc: 'time/colon.png', hour_unit_tc: 'time/colon.png',
      hour_align: ui.align.LEFT,
      minute_zero: 1, minute_follow: 1, minute_array: TIME, minute_space: 0,
      show_level: N,
    })

    // Wochentag (deutsch) über der unteren HP-Leiste
    ui.createWidget(ui.widget.IMG_WEEK, {
      x: X(158), y: Y(250), week_en: WEEK, week_sc: WEEK, week_tc: WEEK, show_level: N,
    })

    // Datum TT.MM unter der HP-Leiste
    ui.createWidget(ui.widget.IMG_DATE, {
      day_startX: X(232), day_startY: Y(298), day_zero: 1, day_space: 0, day_align: ui.align.LEFT,
      day_en_array: DATE, day_sc_array: DATE, day_tc_array: DATE,
      day_unit_en: 'date/dot.png', day_unit_sc: 'date/dot.png', day_unit_tc: 'date/dot.png',
      show_level: N,
    })
    ui.createWidget(ui.widget.IMG_DATE, {
      month_startX: X(289), month_startY: Y(298), month_zero: 1, month_space: 0, month_align: ui.align.LEFT,
      month_en_array: DATE, month_sc_array: DATE, month_tc_array: DATE,
      show_level: N,
    })

    // Schritte unten links
    ui.createWidget(ui.widget.IMG, { x: X(12), y: Y(366), src: 'shoe.png', show_level: N })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: X(36), y: Y(365), w: L(122), h: L(18), font_array: SMALL, h_space: 0,
      align_h: ui.align.LEFT, type: ui.data_type.STEP, show_level: N,
    })

    // Akku unten links
    ui.createWidget(ui.widget.IMG_LEVEL, {
      x: X(14), y: Y(408), image_array: BATT, image_length: 6, type: ui.data_type.BATTERY, show_level: N,
    })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: X(36), y: Y(405), w: L(120), h: L(18), font_array: SMALL, h_space: 0,
      unit_en: 'small/pct.png', unit_sc: 'small/pct.png', unit_tc: 'small/pct.png',
      align_h: ui.align.LEFT, type: ui.data_type.BATTERY, show_level: N,
    })
  },
  onInit() {},
  onDestroy() {},
})
