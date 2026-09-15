"""
Barnaby Bear 3D — Animated Storyteller Avatar
High-fidelity 3D-shaded animated teddy bear with prominent real-time lip-sync,
expressive jaw movement, autonomous eye blinking, and responsive storytelling gestures.
"""
import math
import time
import random
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QRadialGradient, QLinearGradient, QFont
)
from app.audio.lip_sync_engine import VisemeFrame, LipSyncTrack
from app.config.settings import AVATAR_FPS

class BarnabyBearStageWidget(QWidget):
    """
    Renders Barnaby Bear 3D in the right corner stage with highly visible,
    reactive real-time lip-sync, animated jaw, blinking, and storytelling expressions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(240, 280)
        self.setMaximumWidth(320)
        self.setMaximumHeight(360)

        # Audio & Lip-sync tracking
        self.player = None
        self.lip_sync_track: Optional[LipSyncTrack] = None
        self.is_playing = False
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"
        self.narrator_name = "Barnaby Bear"

        # Animation timing
        self.start_time = time.time()
        self.anim_time = 0.0

        # Autonomous blinking
        self.blink_progress = 0.0  # 0.0 = open, 1.0 = fully closed
        self.is_blinking = False
        self.blink_start_time = 0.0
        self.next_blink_interval = random.uniform(2.5, 4.5)
        self.last_blink_time = time.time()

        # Procedural head motion & speech bounce
        self.speech_bounce = 0.0
        self.idle_bob = 0.0
        self.head_tilt = 0.0
        self.brow_lift = 0.0
        self.halo_pulse = 0.0

        # 60 FPS animation loop
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(int(1000 / AVATAR_FPS))
        self.anim_timer.timeout.connect(self._on_animation_tick)
        self.anim_timer.start()

    def set_player_ref(self, player):
        """Store reference to AudioPlayer for 60 FPS direct position querying."""
        self.player = player

    def set_lip_sync_track(self, track: Optional[LipSyncTrack]):
        """Set the pre-computed lip-sync track."""
        self.lip_sync_track = track
        if track:
            frame = track.get_frame(0)
            self.set_viseme_frame(frame)

    def set_viseme_frame(self, frame: VisemeFrame):
        """Direct frame update from audio playback."""
        self.openness = frame.openness
        self.width_factor = frame.width
        self.viseme_type = frame.viseme_type
        self.update()

    def set_speaking_state(self, is_playing: bool):
        """Update active narration state."""
        self.is_playing = is_playing
        if not is_playing:
            self.openness = 0.0
            self.viseme_type = "REST"
        self.update()

    def set_narrator_name(self, name: str):
        self.narrator_name = name
        self.update()

    def reset_avatar(self):
        """Reset avatar to relaxed, smiling pose."""
        self.is_playing = False
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"
        if self.lip_sync_track:
            self.lip_sync_track.reset_smoothing()
        self.update()

    def _on_animation_tick(self):
        """60 FPS continuous update for smooth lip-sync and procedural motion."""
        now = time.time()
        self.anim_time = now - self.start_time

        # 1. Continuous 60 FPS Lip-Sync Polling directly from player
        if self.is_playing and self.player and self.lip_sync_track:
            try:
                # Query player position directly in milliseconds
                pos_ms = self.player.player.position()
                frame = self.lip_sync_track.get_frame(pos_ms)
                # Apply high-gain responsiveness for prominent lip motion
                self.openness = frame.openness
                self.width_factor = frame.width
                self.viseme_type = frame.viseme_type
            except Exception:
                pass

        # 2. Speech bounce & breathing float
        if self.is_playing:
            # Head bobs dynamically with speech openness
            target_bounce = self.openness * 4.0
            self.speech_bounce += (target_bounce - self.speech_bounce) * 0.35
            self.brow_lift += (self.openness * 5.0 - self.brow_lift) * 0.3
            self.head_tilt = math.sin(self.anim_time * 2.5) * (1.2 + self.openness * 2.0)
        else:
            self.speech_bounce *= 0.8
            self.brow_lift *= 0.8
            self.head_tilt = math.sin(self.anim_time * 1.2) * 0.8

        self.idle_bob = math.sin(self.anim_time * 2.0) * 2.5
        self.halo_pulse = (math.sin(self.anim_time * 3.0) + 1.0) * 0.5

        # 3. Autonomous eye blinking
        if not self.is_blinking:
            if now - self.last_blink_time > self.next_blink_interval:
                self.is_blinking = True
                self.blink_start_time = now
                self.next_blink_interval = random.uniform(2.5, 4.8)
        else:
            blink_elapsed = now - self.blink_start_time
            blink_duration = 0.15  # 150ms crisp blink
            if blink_elapsed >= blink_duration:
                self.is_blinking = False
                self.blink_progress = 0.0
                self.last_blink_time = now
            else:
                half = blink_duration / 2.0
                if blink_elapsed < half:
                    self.blink_progress = blink_elapsed / half
                else:
                    self.blink_progress = 1.0 - ((blink_elapsed - half) / half)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        width = self.width()
        height = self.height()
        center_x = width / 2.0
        center_y = height / 2.0 + self.idle_bob - 10 + self.speech_bounce

        # 1. Ambient Stage Glow
        self._draw_ambient_stage(painter, center_x, center_y)

        # 2. Character Body & Storybook Desk
        self._draw_storybook_and_desk(painter, width, height)

        # 3. Head Rig with Dynamic Transform
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.head_tilt)

        self._draw_ears(painter)
        self._draw_head_base(painter)
        self._draw_cheeks(painter)
        self._draw_eyes(painter)
        self._draw_eyebrows(painter)
        self._draw_glasses(painter)
        self._draw_snout_and_mouth(painter)

        painter.restore()

        # 4. Status Badge
        self._draw_status_badge(painter, width, height)

    def _draw_ambient_stage(self, painter: QPainter, cx: float, cy: float):
        """Draw soft warm lighting halo behind Barnaby Bear."""
        radius = 110.0 + (self.halo_pulse * 10.0 if self.is_playing else 0.0)
        halo = QRadialGradient(cx, cy - 10, radius)

        if self.is_playing:
            halo.setColorAt(0.0, QColor(254, 235, 200, 210))  # Warm honey amber
            halo.setColorAt(0.6, QColor(198, 246, 213, 110))  # Soft emerald glow
            halo.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            halo.setColorAt(0.0, QColor(247, 250, 252, 170))
            halo.setColorAt(0.7, QColor(237, 242, 247, 80))
            halo.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QPointF(cx, cy - 10), radius, radius)

    def _draw_storybook_and_desk(self, painter: QPainter, width: int, height: int):
        """Draw the cozy wooden storyteller desk, sweater, and book."""
        cx = width / 2.0
        desk_y = height - 52

        # 1. Emerald Cable-Knit Sweater Torso
        sweater_grad = QLinearGradient(cx, desk_y - 70, cx, desk_y)
        sweater_grad.setColorAt(0.0, QColor(56, 161, 105))   # Emerald 500
        sweater_grad.setColorAt(0.7, QColor(47, 133, 90))    # Emerald 600
        sweater_grad.setColorAt(1.0, QColor(39, 103, 73))    # Deep forest green
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(sweater_grad))
        painter.drawRoundedRect(QRectF(cx - 68, desk_y - 65, 136, 68), 24, 24)

        # Ribbed Turtleneck Collar
        collar_grad = QLinearGradient(cx - 38, desk_y - 70, cx + 38, desk_y - 70)
        collar_grad.setColorAt(0.0, QColor(47, 133, 90))
        collar_grad.setColorAt(0.5, QColor(72, 187, 120))
        collar_grad.setColorAt(1.0, QColor(47, 133, 90))
        painter.setBrush(QBrush(collar_grad))
        painter.drawRoundedRect(QRectF(cx - 36, desk_y - 74, 72, 22), 11, 11)

        # 2. Wooden Table Surface
        table_grad = QLinearGradient(0, desk_y - 10, 0, height)
        table_grad.setColorAt(0.0, QColor(140, 80, 45))     # Warm walnut wood
        table_grad.setColorAt(1.0, QColor(105, 55, 30))
        painter.setBrush(QBrush(table_grad))
        painter.setPen(QPen(QColor(180, 110, 65), 1.5))
        painter.drawRoundedRect(QRectF(10, desk_y - 12, width - 20, 48), 12, 12)

        # 3. "Tales & Wonders" Leather Storybook
        book_rect = QRectF(cx - 60, desk_y - 18, 120, 26)
        book_grad = QLinearGradient(book_rect.left(), book_rect.top(), book_rect.right(), book_rect.bottom())
        book_grad.setColorAt(0.0, QColor(155, 44, 44))     # Deep burgundy leather
        book_grad.setColorAt(1.0, QColor(116, 42, 42))
        painter.setBrush(QBrush(book_grad))
        painter.setPen(QPen(QColor(214, 158, 46), 1.5))    # Golden embossed trim
        painter.drawRoundedRect(book_rect, 6, 6)

        # Book Title Gold Foil Text
        painter.setPen(QPen(QColor(254, 240, 138)))
        font = QFont("Georgia", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(book_rect, Qt.AlignmentFlag.AlignCenter, "✦ TALES & WONDERS ✦")

        # 4. Fluffy Teddy Paws resting on the book
        paw_grad = QRadialGradient(cx - 52, desk_y - 14, 18)
        paw_grad.setColorAt(0.0, QColor(246, 173, 85))
        paw_grad.setColorAt(1.0, QColor(221, 107, 32))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(paw_grad))
        painter.drawEllipse(QPointF(cx - 52, desk_y - 14), 16, 12)

        paw_grad_r = QRadialGradient(cx + 52, desk_y - 14, 18)
        paw_grad_r.setColorAt(0.0, QColor(246, 173, 85))
        paw_grad_r.setColorAt(1.0, QColor(221, 107, 32))
        painter.setBrush(QBrush(paw_grad_r))
        painter.drawEllipse(QPointF(cx + 52, desk_y - 14), 16, 12)

    def _draw_ears(self, painter: QPainter):
        """Draw fluffy teddy bear ears with 3D radial shading."""
        # Left Ear
        left_ear = QRadialGradient(-58, -62, 28)
        left_ear.setColorAt(0.0, QColor(251, 211, 141))
        left_ear.setColorAt(0.7, QColor(237, 137, 54))
        left_ear.setColorAt(1.0, QColor(192, 86, 33))
        painter.setPen(QPen(QColor(156, 66, 33), 2.2))
        painter.setBrush(QBrush(left_ear))
        painter.drawEllipse(QPointF(-58, -62), 26, 26)

        # Inner ear pink
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(254, 215, 215)))
        painter.drawEllipse(QPointF(-58, -62), 15, 15)

        # Right Ear
        right_ear = QRadialGradient(58, -62, 28)
        right_ear.setColorAt(0.0, QColor(251, 211, 141))
        right_ear.setColorAt(0.7, QColor(237, 137, 54))
        right_ear.setColorAt(1.0, QColor(192, 86, 33))
        painter.setPen(QPen(QColor(156, 66, 33), 2.2))
        painter.setBrush(QBrush(right_ear))
        painter.drawEllipse(QPointF(58, -62), 26, 26)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(254, 215, 215)))
        painter.drawEllipse(QPointF(58, -62), 15, 15)

    def _draw_head_base(self, painter: QPainter):
        """Draw Barnaby Bear's spherical 3D shaded head."""
        head_grad = QRadialGradient(0, -25, 78)
        head_grad.setColorAt(0.0, QColor(254, 235, 200))   # Top highlight
        head_grad.setColorAt(0.4, QColor(246, 173, 85))    # Warm honey fur
        head_grad.setColorAt(0.85, QColor(221, 107, 32))   # Deep fur shadow
        head_grad.setColorAt(1.0, QColor(192, 86, 33))

        painter.setPen(QPen(QColor(156, 66, 33), 2.4))
        painter.setBrush(QBrush(head_grad))
        painter.drawRoundedRect(QRectF(-70, -78, 140, 138), 65, 62)

    def _draw_cheeks(self, painter: QPainter):
        """Draw cute blushing cheeks."""
        blush = QRadialGradient(-46, 2, 18)
        blush.setColorAt(0.0, QColor(254, 178, 178, 190))
        blush.setColorAt(1.0, QColor(254, 178, 178, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(blush))
        painter.drawEllipse(QPointF(-46, 2), 18, 14)

        blush_r = QRadialGradient(46, 2, 18)
        blush_r.setColorAt(0.0, QColor(254, 178, 178, 190))
        blush_r.setColorAt(1.0, QColor(254, 178, 178, 0))
        painter.setBrush(QBrush(blush_r))
        painter.drawEllipse(QPointF(46, 2), 18, 14)

    def _draw_eyes(self, painter: QPainter):
        """Draw expressive glossy hazel eyes with natural eyelid blinks."""
        eye_y = -22.0
        eye_spacing = 30.0
        eye_w = 17.0
        eye_h = 22.0

        for eye_x in [-eye_spacing, eye_spacing]:
            # White Sclera
            painter.setPen(QPen(QColor(203, 213, 225), 1.0))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(eye_x, eye_y), eye_w, eye_h)

            # Warm Golden Hazel Iris & Pupil
            pupil_y = eye_y + (1.2 if self.is_playing else 0.0)
            iris_grad = QRadialGradient(eye_x, pupil_y, 11)
            iris_grad.setColorAt(0.0, QColor(26, 32, 44))     # Black pupil center
            iris_grad.setColorAt(0.65, QColor(116, 66, 16))   # Warm hazel rim
            iris_grad.setColorAt(1.0, QColor(45, 55, 72))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(iris_grad))
            painter.drawEllipse(QPointF(eye_x, pupil_y), 12, 14)

            # Bright Catchlights (Sparkles)
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            painter.drawEllipse(QPointF(eye_x - 3.8, pupil_y - 4.5), 5.0, 5.0)
            painter.drawEllipse(QPointF(eye_x + 3.2, pupil_y + 3.0), 2.5, 2.5)

            # Blinking Eyelid
            if self.blink_progress > 0.02:
                lid_grad = QLinearGradient(eye_x, eye_y - eye_h, eye_x, eye_y + eye_h)
                lid_grad.setColorAt(0.0, QColor(246, 173, 85))
                lid_grad.setColorAt(1.0, QColor(221, 107, 32))
                painter.setPen(QPen(QColor(156, 66, 33), 1.8))
                painter.setBrush(QBrush(lid_grad))

                closure_h = eye_h * 2.0 * self.blink_progress
                path = QPainterPath()
                path.addEllipse(QPointF(eye_x, eye_y), eye_w, eye_h)

                lid_rect = QRectF(eye_x - eye_w - 2, eye_y - eye_h, (eye_w + 2) * 2, closure_h)
                painter.save()
                painter.setClipPath(path)
                painter.drawRect(lid_rect)
                painter.restore()

    def _draw_eyebrows(self, painter: QPainter):
        """Draw expressive animated teddy eyebrows that emote with speech."""
        lift = -self.brow_lift
        brow_pen = QPen(QColor(116, 42, 42), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(brow_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Left Eyebrow
        left_p = QPainterPath()
        left_p.moveTo(-42, -44 + lift)
        left_p.quadTo(-30, -52 + lift, -18, -45 + lift)
        painter.drawPath(left_p)

        # Right Eyebrow
        right_p = QPainterPath()
        right_p.moveTo(18, -45 + lift)
        right_p.quadTo(30, -52 + lift, 42, -44 + lift)
        painter.drawPath(right_p)

    def _draw_glasses(self, painter: QPainter):
        """Draw Barnaby Bear's iconic round scholar glasses."""
        glasses_pen = QPen(QColor(214, 158, 46), 2.6)  # Warm brass gold wire
        painter.setPen(glasses_pen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 35)))  # Subtle lens glare

        # Left Lens
        painter.drawEllipse(QPointF(-30, -22), 22, 22)
        # Right Lens
        painter.drawEllipse(QPointF(30, -22), 22, 22)
        # Bridge
        painter.drawLine(-8, -22, 8, -22)
        # Glare arc on lenses
        glare_pen = QPen(QColor(255, 255, 255, 140), 1.6)
        painter.setPen(glare_pen)
        painter.drawArc(QRectF(-46, -38, 18, 18), 45 * 16, 90 * 16)
        painter.drawArc(QRectF(14, -38, 18, 18), 45 * 16, 90 * 16)

    def _draw_snout_and_mouth(self, painter: QPainter):
        """
        Draw Barnaby Bear's cream snout and dynamic animated jaw with
        highly visible real-time lip-sync (REST, AA, OO, EE, MBP).
        """
        openness = self.openness if self.is_playing else 0.0

        # Snout Base (Creamy warm oval)
        snout_grad = QRadialGradient(0, -2, 45)
        snout_grad.setColorAt(0.0, QColor(255, 253, 225))
        snout_grad.setColorAt(0.75, QColor(254, 235, 200))
        snout_grad.setColorAt(1.0, QColor(246, 205, 150))

        painter.setPen(QPen(QColor(192, 86, 33), 2.0))
        painter.setBrush(QBrush(snout_grad))
        # Snout stretches subtly with speech openness
        snout_h = 56.0 + (openness * 8.0)
        painter.drawRoundedRect(QRectF(-48, -14, 96, snout_h), 46, 34)

        # Chocolate Button Nose
        nose_grad = QRadialGradient(0, -3, 15)
        nose_grad.setColorAt(0.0, QColor(116, 42, 42))
        nose_grad.setColorAt(0.8, QColor(67, 24, 24))
        nose_grad.setColorAt(1.0, QColor(44, 15, 15))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(nose_grad))
        painter.drawRoundedRect(QRectF(-14, -10, 28, 18), 10, 8)

        # Nose highlight glint
        painter.setBrush(QBrush(QColor(255, 255, 255, 210)))
        painter.drawEllipse(QPointF(-3.5, -6), 4.5, 2.5)

        # Philtrum line from nose to mouth
        line_pen = QPen(QColor(116, 42, 42), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(line_pen)
        painter.drawLine(0, 8, 0, 16)

        # ==========================================================
        # REAL-TIME DYNAMIC LIP-SYNC MOUTH (PROMINENT & REACTIVE!)
        # ==========================================================
        mouth_y = 16.0

        if openness < 0.08:
            # REST POSE: Charming double teddy bear smile
            painter.setPen(QPen(QColor(116, 42, 42), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            smile_l = QPainterPath()
            smile_l.moveTo(-16, 14)
            smile_l.quadTo(-8, mouth_y + 6, 0, mouth_y)
            painter.drawPath(smile_l)

            smile_r = QPainterPath()
            smile_r.moveTo(0, mouth_y)
            smile_r.quadTo(8, mouth_y + 6, 16, 14)
            painter.drawPath(smile_r)
            return

        # ACTIVE SPEECH: Dynamic open mouth cavity
        # Width scales with viseme (wider for EE/AA, narrower for OO)
        half_w = 15.0 * (0.65 + self.width_factor * 0.85)
        # Height scales dynamically from 6px to 26px based on audio openness
        open_h = max(6.0, openness * 28.0)

        cavity = QPainterPath()
        top_y = mouth_y
        bot_y = mouth_y + open_h

        cavity.moveTo(-half_w, top_y)
        cavity.quadTo(0, top_y - (open_h * 0.2), half_w, top_y)
        cavity.quadTo(0, bot_y + (open_h * 0.35), -half_w, top_y)

        # 1. Inner mouth cavity (Deep burgundy / crimson)
        painter.setPen(QPen(QColor(116, 42, 42), 2.2))
        painter.setBrush(QBrush(QColor(74, 14, 24)))
        painter.drawPath(cavity)

        # 2. Cute white teeth (shows when mouth opens wide e.g. for "EE" or "AA")
        if (self.viseme_type in ["EE", "AA"] or openness > 0.45) and open_h > 8.0:
            painter.save()
            painter.setClipPath(cavity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
            teeth_w = half_w * 1.3
            painter.drawRoundedRect(QRectF(-teeth_w / 2.0, top_y - 2, teeth_w, 8.0), 3, 3)
            painter.restore()

        # 3. Bouncy pink teddy tongue
        painter.save()
        painter.setClipPath(cavity)
        painter.setPen(Qt.PenStyle.NoPen)
        tongue_color = QColor(245, 101, 101)  # Warm playful pink
        painter.setBrush(QBrush(tongue_color))
        tongue_w = half_w * 1.15
        tongue_h = open_h * 0.55
        painter.drawEllipse(QPointF(0, bot_y + 2), tongue_w * 0.6, tongue_h)
        painter.restore()

        # Outline lips
        painter.setPen(QPen(QColor(116, 42, 42), 2.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(cavity)

    def _draw_status_badge(self, painter: QPainter, width: int, height: int):
        """Draw storytelling status badge at the bottom of the stage."""
        badge_w = min(width - 36, 220)
        badge_h = 28
        badge_x = (width - badge_w) / 2.0
        badge_y = height - 34
        badge_rect = QRectF(badge_x, badge_y, badge_w, badge_h)

        painter.setPen(Qt.PenStyle.NoPen)
        if self.is_playing:
            # Warm glowing emerald & gold badge
            painter.setBrush(QBrush(QColor(47, 133, 90, 225)))
            text = "✨ Barnaby Reading to You..."
            text_color = QColor(255, 255, 255)
        else:
            painter.setBrush(QBrush(QColor(45, 55, 72, 195)))
            text = "📖 Ready for Story"
            text_color = QColor(247, 250, 252)

        painter.drawRoundedRect(badge_rect, 14, 14)

        painter.setPen(QPen(text_color))
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
