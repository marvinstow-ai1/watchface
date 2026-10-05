import ui from '@zos/ui'
import * as zui from '@zos/ui' // Namespace-Import wie in Zepps Vorlagen (für die Animation)

const N = ui.show_level.ONLY_NORMAL

// Kompaktes Design (390 x DESIGN_H, aus dem Original neu zusammengesetzt), verkleinert und
// mittig, damit die runden Ecken nichts abschneiden. Koordinaten unten sind Design-Koordinaten;
// alles ab Gengar (Original-y >= 226) liegt um BOTTOM_DY höher als im Original.
// Der Block wird von tools/inset_layout.py gesetzt (die Assets sind dort bereits verkleinert).
// ANIM (nur Battle-Watchfaces): animierte Monster statt Lugia/Gengar, Frames in assets/anim/.
// <generated: tools/inset_layout.py>
const SCALE = 0.92
const DESIGN_H = 378
const BOTTOM_DY = -72
const ANIM = null
// </generated>
const OX = Math.floor((390 - Math.round(390 * SCALE)) / 2)
const OY = Math.floor((450 - Math.round(DESIGN_H * SCALE)) / 2)
const X = (x) => OX + Math.round(x * SCALE)
const Y = (y) => OY + Math.round(y * SCALE)
const YB = (y) => Y(y + BOTTOM_DY) // untere Hälfte: Original-y angeben
const L = (v) => Math.round(v * SCALE)
const arr = (dir) => [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => `${dir}/${n}.png`)
const TIME = arr('time')
const SEC = arr('sec')
const DATE = arr('date')
const SMALL = arr('small')
const WEEK = [1, 2, 3, 4, 5, 6, 7].map((n) => `week/${n}.png`)
const BATT = [0, 1, 2, 3, 4, 5].map((n) => `batt/${n}.png`)

WatchFace({
  build() {
    ui.createWidget(ui.widget.IMG, { x: 0, y: 0, src: 'bg.png', show_level: N })

    // Animierte Monster (Battle-Watchfaces): Endlosschleife, nur bei aktivem Display.
    // Abgesichert: scheitert etwas, läuft das restliche Zifferblatt weiter und der Fehler
    // steht klein unten auf dem Display (zur Diagnose).
    if (ANIM) {
      try {
        const AS = zui.anim_status || ui.anim_status || {}
        const START = AS.START !== undefined ? AS.START : 1
        const STOP = AS.STOP !== undefined ? AS.STOP : 3
        const PROP = zui.prop || ui.prop || {}
        const ANIM_PROP = PROP.ANIM_STATUS
        const W = zui.widget || ui.widget
        const anims = []
        for (const key of ['top', 'bottom']) {
          const a = ANIM[key]
          if (!a) continue
          const w = (zui.createWidget || ui.createWidget)(W.IMG_ANIM, {
            x: a.x, y: a.y, anim_path: 'anim', anim_prefix: key, anim_ext: 'png', // Bildschirm-Pixel
            anim_fps: a.fps, anim_size: a.frames, repeat_count: 0, // 0 = Endlosschleife
            anim_status: STOP, show_level: N,
          })
          if (ANIM_PROP !== undefined) w.setProperty(ANIM_PROP, START)
          anims.push(w)
        }
        if (anims.length && ANIM_PROP !== undefined && W.WIDGET_DELEGATE) {
          // nach dem Aufwecken des Displays wieder starten
          ui.createWidget(W.WIDGET_DELEGATE, {
            resume_call: () => anims.forEach((w) => w.setProperty(ANIM_PROP, START)),
            pause_call: () => anims.forEach((w) => w.setProperty(ANIM_PROP, STOP)),
          })
        }
      } catch (e) {
        ui.createWidget(ui.widget.TEXT, {
          x: 10, y: 425, w: 370, h: 24, color: 0xcc0000, text_size: 16,
          text: 'ANIM: ' + (e && e.message ? e.message : String(e)), show_level: N,
        })
      }
    }

    // Uhrzeit oben links (24h), Ziffern 48x36 statt 40x30;
    // Sekunden klein (24x18) oben rechts neben den Minuten
    const HH_MM_W = 4 * L(48) + L(18) // tatsächliche Breite der verkleinerten Bilder
    ui.createWidget(ui.widget.IMG_TIME, {
      hour_zero: 1, hour_startX: X(20), hour_startY: Y(0), hour_array: TIME, hour_space: 0,
      hour_unit_en: 'time/colon.png', hour_unit_sc: 'time/colon.png', hour_unit_tc: 'time/colon.png',
      hour_align: ui.align.LEFT,
      minute_zero: 1, minute_follow: 1, minute_array: TIME, minute_space: 0,
      second_zero: 1, second_startX: X(20) + HH_MM_W + L(4), second_startY: Y(0),
      second_array: SEC, second_space: 0,
      show_level: N,
    })

    // Wochentag (deutsch) über der unteren HP-Leiste, rechtsbündig mit dem Ende der HP-Leiste (x=368)
    ui.createWidget(ui.widget.IMG_WEEK, {
      x: X(369 - 222), y: YB(250), week_en: WEEK, week_sc: WEEK, week_tc: WEEK, show_level: N,
    })

    // Datum TT.MM unter der HP-Leiste; Punkt als eigenes Bild mit festem Abstand
    // (als day_unit landete er auf der Uhr in der Monatszahl)
    ui.createWidget(ui.widget.IMG_DATE, {
      day_startX: X(232), day_startY: YB(298), day_zero: 1, day_space: 0, day_align: ui.align.LEFT,
      day_en_array: DATE, day_sc_array: DATE, day_tc_array: DATE,
      show_level: N,
    })
    ui.createWidget(ui.widget.IMG, { x: X(282), y: YB(298), src: 'date/dot.png', show_level: N })
    ui.createWidget(ui.widget.IMG_DATE, {
      month_startX: X(290), month_startY: YB(298), month_zero: 1, month_space: 0, month_align: ui.align.LEFT,
      month_en_array: DATE, month_sc_array: DATE, month_tc_array: DATE,
      show_level: N,
    })

    // Box unten links (innen x 12-161, y 351-437): Symbol + Zahl, zwei gleichmäßig verteilte Zeilen.
    // Symbole sind so groß wie eine Ziffer (24x18), Ziffern 23px breit -> 5-stellige Schritte passen.
    // Schritte
    ui.createWidget(ui.widget.IMG, { x: X(17), y: YB(368), src: 'shoe.png', show_level: N })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: X(45), y: YB(368), w: L(115), h: L(18), font_array: SMALL, h_space: 0,
      align_h: ui.align.LEFT, type: ui.data_type.STEP, show_level: N,
    })

    // Akku
    ui.createWidget(ui.widget.IMG_LEVEL, {
      x: X(17), y: YB(403), image_array: BATT, image_length: 6, type: ui.data_type.BATTERY, show_level: N,
    })
    ui.createWidget(ui.widget.TEXT_IMG, {
      x: X(45), y: YB(403), w: L(115), h: L(18), font_array: SMALL, h_space: 0,
      unit_en: 'small/pct.png', unit_sc: 'small/pct.png', unit_tc: 'small/pct.png',
      align_h: ui.align.LEFT, type: ui.data_type.BATTERY, show_level: N,
    })
  },
  onInit() {},
  onDestroy() {},
})
