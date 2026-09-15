"""
Animated Storyteller Avatar Widget
High-DPI vector-rendered kid-friendly character with real-time lip-sync,
autonomous eye-blinking, and smooth idle breathing motion.
"""
import math
import random
import time
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QRadialGradient, QLinearGradient, QFont
)
from app.audio.lip_sync_engine import VisemeFrame
from app.config.settings import AVATAR_FPS

class AvatarStageWidget(QWidget):
    """
    Renders an interactive storyteller avatar that responds dynamically
    to audio lip-sync frames and playback states.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 210)
        self.setMaximumHeight(260)

        # State attributes
        self.is_playing = False
        self.current_frame = VisemeFrame(0, 0.0, 0.5, "REST")
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"

        # Animation timing
        self.start_time = time.time()
        self.anim_time = 0.0

        # Eye blink state machine
        self.blink_progress = 0.0  # 0.0 = open, 1.0 = fully closed
        self.is_blinking = False
        self.blink_start_time = 0.0
        self.next_blink_interval = random.uniform(2.5, 4.5)
        self.last_blink_time = time.time()

        # Head / body idle physics
        self.idle_bob = 0.0
        self.head_tilt = 0.0
        self.halo_pulse = 0.0

        # 60 FPS animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(int(1000 / AVATAR_FPS))
        self.anim_timer.timeout.connect(self._on_animation_tick)
        self.anim_timer.start()

    def set_viseme_frame(self, frame: VisemeFrame):
        """Update current lip-sync viseme target from audio playback."""
        self.current_frame = frame
        self.openness = frame.openness
        self.width_factor = frame.width
        self.viseme_type = frame.viseme_type
        self.update()

    def set_speaking_state(self, is_playing: bool):
        """Set whether the story is currently playing (speaking) or paused/stopped."""
        self.is_playing = is_playing
        if not is_playing:
            self.openness = 0.0
            self.viseme_type = "REST"
        self.update()

    def reset_avatar(self):
        """Reset avatar to relaxed rest pose."""
        self.is_playing = False
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"
        self.update()

    def _on_animation_tick(self):
        """Update continuous procedural motion (blinking, breathing, micro-sway)."""
        now = time.time()
        self.anim_time = now - self.start_time

        # 1. Idle breathing & float (gentle sine wave)
        # 1.5 rad/s gives a calm ~4-second breathing cycle
        self.idle_bob = math.sin(self.anim_time * 2.2) * 3.5
        self.head_tilt = math.sin(self.anim_time * 1.4) * 1.2
        self.halo_pulse = (math.sin(self.anim_time * 3.0) + 1.0) * 0.5

        # 2. Autonomous eye blinking
        if not self.is_blinking:
            if now - self.last_blink_time > self.next_blink_interval:
                self.is_blinking = True
                self.blink_start_time = now
                self.next_blink_interval = random.uniform(2.5, 5.0)
        else:
            blink_elapsed = now - self.blink_start_time
            blink_duration = 0.16  # 160ms total blink
            if blink_elapsed >= blink_duration:
                self.is_blinking = False
                self.blink_progress = 0.0
                self.last_blink_time = now
            else:
                # Triangular curve: 0 -> 1 -> 0
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
        center_y = height / 2.0 + self.idle_bob - 8

        # 1. Draw Ambient Stage Halo Glow
        self._draw_ambient_stage(painter, center_x, center_y)

        # 2. Draw Character
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.head_tilt)

        self._draw_ears(painter)
        self._draw_head_and_body(painter)
        self._draw_cheeks(painter)
        self._draw_eyes(painter)
        self._draw_eyebrows(painter)
        self._draw_nose(painter)
        self._draw_mouth(painter)
        self._draw_storyteller_badge(painter)

        painter.restore()

        # 3. Draw Speaking Status Badge
        self._draw_status_indicator(painter, width, height)

    def _draw_ambient_stage(self, painter: QPainter, cx: float, cy: float):
        """Draw soft glowing halo behind avatar."""
        radius = 95.0 + (self.halo_pulse * 8.0 if self.is_playing else 0.0)
        halo = QRadialGradient(cx, cy - 10, radius)

        if self.is_playing:
            halo.setColorAt(0.0, QColor(254, 235, 200, 190))  # Warm amber glow
            halo.setColorAt(0.65, QColor(235, 248, 255, 120))  # Soft sky glow
            halo.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            halo.setColorAt(0.0, QColor(237, 242, 247, 160))  # Relaxed neutral glow
            halo.setColorAt(0.7, QColor(247, 250, 252, 90))
            halo.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QPointF(cx, cy - 10), radius, radius)

    def _draw_ears(self, painter: QPainter):
        """Draw cute rounded storyteller ears with soft inner shading."""
        # Outer ear color
        ear_color = QColor(246, 173, 85)       # Amber 400
        inner_ear = QColor(254, 215, 215)       # Soft pink
        outline_pen = QPen(QColor(221, 107, 32), 2.2)

        # Left Ear
        painter.setPen(outline_pen)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(QPointF(-62, -55), 26, 26)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(inner_ear))
        painter.drawEllipse(QPointF(-62, -55), 15, 15)

        # Right Ear
        painter.setPen(outline_pen)
        painter.setBrush(QBrush(ear_color))
        painter.drawEllipse(QPointF(62, -55), 26, 26)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(inner_ear))
        painter.drawEllipse(QPointF(62, -55), 15, 15)

    def _draw_head_and_body(self, painter: QPainter):
        """Draw warm, rounded head and cozy collar."""
        # Collar / Shirt peeking
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(72, 187, 120)))  # Storyteller green sweater
        painter.drawRoundedRect(QRectF(-48, 54, 96, 38), 16, 16)

        # Head Base with subtle 3D vertical gradient
        head_grad = QLinearGradient(0, -75, 0, 65)
        head_grad.setColorAt(0.0, QColor(251, 211, 141))  # Amber 300
        head_grad.setColorAt(0.7, QColor(246, 173, 85))   # Amber 400
        head_grad.setColorAt(1.0, QColor(237, 137, 54))   # Amber 500

        painter.setPen(QPen(QColor(221, 107, 32), 2.5))
        painter.setBrush(QBrush(head_grad))
        painter.drawRoundedRect(QRectF(-68, -68, 136, 132), 62, 58)

        # Creamy muzzle/tummy patch
        muzzle_grad = QLinearGradient(0, -10, 0, 50)
        muzzle_grad.setColorAt(0.0, QColor(254, 252, 191))
        muzzle_grad.setColorAt(1.0, QColor(254, 235, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(muzzle_grad))
        painter.drawRoundedRect(QRectF(-44, -12, 88, 62), 40, 30)

    def _draw_cheeks(self, painter: QPainter):
        """Draw friendly blushing cheeks."""
        cheek_color = QColor(254, 178, 178, 160)  # Rosy pink blush
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(cheek_color))
        painter.drawEllipse(QPointF(-44, 12), 14, 9)
        painter.drawEllipse(QPointF(44, 12), 14, 9)

    def _draw_eyes(self, painter: QPainter):
        """Draw expressive eyes with shiny catchlights and animated blinking eyelids."""
        eye_y = -16.0
        eye_spacing = 28.0
        eye_width = 15.0
        eye_height = 20.0

        for eye_x in [-eye_spacing, eye_spacing]:
            # Eye Sclera (White)
            painter.setPen(QPen(QColor(203, 213, 225), 1.0))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(eye_x, eye_y), eye_width, eye_height)

            # Iris & Pupil (Warm deep chocolate/hazel)
            pupil_y = eye_y + (1.0 if self.is_playing else 0.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(45, 55, 72)))
            painter.drawEllipse(QPointF(eye_x, pupil_y), 11, 13)

            # Highlight / Sparkle (Catchlights)
            painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
            painter.drawEllipse(QPointF(eye_x - 3.5, pupil_y - 4.5), 4.5, 4.5)
            painter.drawEllipse(QPointF(eye_x + 3.0, pupil_y + 2.5), 2.2, 2.2)

            # Animated Eyelid for Blinking
            if self.blink_progress > 0.01:
                eyelid_color = QColor(246, 173, 85)
                painter.setPen(QPen(QColor(221, 107, 32), 1.8))
                painter.setBrush(QBrush(eyelid_color))

                # Eyelid descends from top of eye socket
                closure_h = eye_height * 2.0 * self.blink_progress
                path = QPainterPath()
                path.addEllipse(QPointF(eye_x, eye_y), eye_width, eye_height)

                lid_rect = QRectF(eye_x - eye_width - 2, eye_y - eye_height,
                                  (eye_width + 2) * 2, closure_h)
                
                painter.save()
                painter.setClipPath(path)
                painter.drawRect(lid_rect)
                painter.restore()

    def _draw_eyebrows(self, painter: QPainter):
        """Draw cute animated eyebrows that lift when excited/speaking."""
        lift = -3.5 if (self.is_playing and self.openness > 0.4) else 0.0
        brow_pen = QPen(QColor(156, 66, 33), 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(brow_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Left Eyebrow
        left_path = QPainterPath()
        left_path.moveTo(-38, -36 + lift)
        left_path.quadTo(-28, -42 + lift, -18, -37 + lift)
        painter.drawPath(left_path)

        # Right Eyebrow
        right_path = QPainterPath()
        right_path.moveTo(18, -37 + lift)
        right_path.quadTo(28, -42 + lift, 38, -36 + lift)
        painter.drawPath(right_path)

    def _draw_nose(self, painter: QPainter):
        """Draw button nose."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(116, 42, 42)))
        painter.drawRoundedRect(QRectF(-8, -4, 16, 10), 6, 6)

    def _draw_mouth(self, painter: QPainter):
        """
        Draw dynamic mouth that morphs into visemes (REST, AA, OO, EE, MBP)
        based on real-time audio lip-sync parameters.
        """
        mouth_y = 18.0
        openness = self.openness if self.is_playing else 0.0

        if openness < 0.08:
            # REST POSE: Cheerful resting smile curve
            pen = QPen(QColor(156, 66, 33), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            smile = QPainterPath()
            smile.moveTo(-16, mouth_y)
            smile.quadTo(0, mouth_y + 11, 16, mouth_y)
            painter.drawPath(smile)
            return

        # SPEAKING POSE: Calculate dynamic mouth dimensions
        base_half_w = 14.0 * (0.6 + self.width_factor * 0.8)
        open_h = max(6.0, openness * 26.0)

        # Mouth Cavity Path
        cavity = QPainterPath()
        top_y = mouth_y - (open_h * 0.25)
        bot_y = mouth_y + (open_h * 0.75)

        cavity.moveTo(-base_half_w, mouth_y)
        cavity.quadTo(0, top_y, base_half_w, mouth_y)
        cavity.quadTo(0, bot_y + (open_h * 0.3), -base_half_w, mouth_y)

        # 1. Fill inner mouth cavity (deep dark burgundy)
        painter.setPen(QPen(QColor(156, 66, 33), 2.0))
        painter.setBrush(QBrush(QColor(74, 14, 24)))
        painter.drawPath(cavity)

        # 2. Draw Teeth if open enough (e.g. for "EE" or "AA")
        if self.viseme_type in ["EE", "AA"] and open_h > 10.0:
            painter.save()
            painter.setClipPath(cavity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
            painter.drawRoundedRect(QRectF(-base_half_w * 0.65, top_y - 2, base_half_w * 1.3, 8), 3, 3)
            painter.restore()

        # 3. Draw cute pink tongue
        painter.save()
        painter.setClipPath(cavity)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(245, 101, 101)))
        tongue_w = base_half_w * 1.2
        painter.drawEllipse(QPointF(0, bot_y + 2), tongue_w * 0.55, open_h * 0.45)
        painter.restore()

    def _draw_storyteller_badge(self, painter: QPainter):
        """Draw cute storyteller spectacles or bow tie."""
        # Storyteller round glasses
        glasses_pen = QPen(QColor(113, 128, 150, 180), 2.0)
        painter.setPen(glasses_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(-28, -16), 18, 18)
        painter.drawEllipse(QPointF(28, -16), 18, 18)
        # Bridge
        painter.drawLine(-10, -16, 10, -16)

    def _draw_status_indicator(self, painter: QPainter, width: int, height: int):
        """Draw a pill-shaped status label indicating storyteller state."""
        badge_y = height - 22
        badge_w = 160
        badge_x = (width - badge_w) / 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        if self.is_playing:
            painter.setBrush(QBrush(QColor(235, 248, 255, 220)))  # Soft blue
            text = "✨ Narrating Story..."
            text_color = QColor(43, 108, 176)
        else:
            painter.setBrush(QBrush(QColor(247, 250, 252, 200)))
            text = "📖 Ready to Listen"
            text_color = QColor(113, 128, 150)

        painter.drawRoundedRect(QRectF(badge_x, badge_y, badge_w, 20), 10, 10)

        painter.setPen(QPen(text_color))
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(badge_x, badge_y, badge_w, 20), Qt.AlignmentFlag.AlignCenter, text)
