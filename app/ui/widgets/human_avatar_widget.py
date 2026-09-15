"""
3D Stylized Human Narrator Avatar Widget ("Papa / Mama Storyteller")
Renders the Concept 2 3D character with real-time lip-sync mouth morphing,
autonomous eye-blinking, and gentle breathing/idle animation.
"""
import os
import math
import time
import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QPixmap, QRadialGradient, QLinearGradient, QFont
)
from app.audio.lip_sync_engine import VisemeFrame
from app.config.settings import AVATAR_FPS

class HumanAvatarStageWidget(QWidget):
    """
    Renders the 3D Stylized Human Narrator in a right-corner card
    with real-time lip-sync and life-like idle motion.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 260)
        self.setMaximumWidth(320)
        self.setMaximumHeight(360)

        # Asset path
        self.asset_path = "data/avatars/human_narrator.jpg"
        self.base_pixmap = None
        if os.path.exists(self.asset_path):
            self.base_pixmap = QPixmap(self.asset_path)

        # State attributes
        self.is_playing = False
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"
        self.narrator_name = "Papa Storyteller"

        # Animation timing
        self.start_time = time.time()
        self.anim_time = 0.0

        # Autonomous blinking
        self.blink_progress = 0.0  # 0.0 (open) to 1.0 (closed)
        self.is_blinking = False
        self.blink_start_time = 0.0
        self.next_blink_interval = random.uniform(2.5, 4.5)
        self.last_blink_time = time.time()

        # Idle motion
        self.idle_bob = 0.0
        self.head_tilt = 0.0
        self.halo_pulse = 0.0

        # 60 FPS animation loop
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(int(1000 / AVATAR_FPS))
        self.anim_timer.timeout.connect(self._on_animation_tick)
        self.anim_timer.start()

    def set_viseme_frame(self, frame: VisemeFrame):
        """Update lip-sync targets from the audio engine."""
        self.openness = frame.openness
        self.width_factor = frame.width
        self.viseme_type = frame.viseme_type
        self.update()

    def set_speaking_state(self, is_playing: bool):
        """Set playing/speaking state."""
        self.is_playing = is_playing
        if not is_playing:
            self.openness = 0.0
            self.viseme_type = "REST"
        self.update()

    def set_narrator_name(self, name: str):
        """Update the displayed narrator label."""
        self.narrator_name = name
        self.update()

    def reset_avatar(self):
        """Reset avatar to relaxed smile."""
        self.is_playing = False
        self.openness = 0.0
        self.width_factor = 0.5
        self.viseme_type = "REST"
        self.update()

    def _on_animation_tick(self):
        """Tick procedural animations (blinking, breathing, glowing)."""
        now = time.time()
        self.anim_time = now - self.start_time

        # 1. Gentle breathing bob (±2.5px) and subtle head tilt
        self.idle_bob = math.sin(self.anim_time * 2.0) * 2.5
        self.head_tilt = math.sin(self.anim_time * 1.3) * 0.8
        self.halo_pulse = (math.sin(self.anim_time * 2.8) + 1.0) * 0.5

        # 2. Autonomous blinking
        if not self.is_blinking:
            if now - self.last_blink_time > self.next_blink_interval:
                self.is_blinking = True
                self.blink_start_time = now
                self.next_blink_interval = random.uniform(2.5, 5.0)
        else:
            blink_elapsed = now - self.blink_start_time
            blink_duration = 0.16  # 160ms blink
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

        # Portrait card dimensions
        card_margin = 12
        card_w = min(width - card_margin * 2, 280)
        card_h = min(height - card_margin * 2, 310)
        card_x = (width - card_w) / 2.0
        card_y = (height - card_h) / 2.0 + self.idle_bob

        card_rect = QRectF(card_x, card_y, card_w, card_h)

        # 1. Draw Ambient Outer Glow
        self._draw_ambient_glow(painter, card_rect)

        # 2. Draw 3D Character Portrait
        self._draw_character_card(painter, card_rect)

        # 3. Draw Lip-Sync Mouth & Facial Animation Overlay
        self._draw_face_animation_overlay(painter, card_rect)

        # 4. Draw Speaking Status Badge
        self._draw_status_badge(painter, card_rect)

    def _draw_ambient_glow(self, painter: QPainter, card_rect: QRectF):
        """Draw warm library glowing halo behind the card."""
        cx = card_rect.center().x()
        cy = card_rect.center().y()
        radius = card_rect.width() * 0.72 + (self.halo_pulse * 6.0 if self.is_playing else 0.0)

        glow = QRadialGradient(cx, cy, radius)
        if self.is_playing:
            glow.setColorAt(0.0, QColor(254, 215, 160, 180))  # Warm amber
            glow.setColorAt(0.7, QColor(235, 248, 255, 90))   # Soft blue
            glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            glow.setColorAt(0.0, QColor(237, 242, 247, 140))
            glow.setColorAt(0.75, QColor(255, 255, 255, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_character_card(self, painter: QPainter, card_rect: QRectF):
        """Render the 3D human character portrait inside a rounded container."""
        # Rounded clipping path
        card_path = QPainterPath()
        card_path.addRoundedRect(card_rect, 20, 20)

        painter.save()
        painter.setClipPath(card_path)

        if self.base_pixmap and not self.base_pixmap.isNull():
            # Zoom slightly to crop nicely onto head/torso
            # Source image is 1024x1024. Head & upper chest center ~ (512, 420)
            src_w = 780
            src_h = 780
            src_x = (self.base_pixmap.width() - src_w) / 2
            src_y = int(self.base_pixmap.height() * 0.04)
            src_rect = QRectF(src_x, src_y, src_w, src_h)

            painter.drawPixmap(card_rect.toRect(), self.base_pixmap, src_rect.toRect())
        else:
            # Fallback warm gradient if asset not loaded
            grad = QLinearGradient(card_rect.topLeft(), card_rect.bottomLeft())
            grad.setColorAt(0.0, QColor(251, 211, 141))
            grad.setColorAt(1.0, QColor(221, 107, 32))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(card_rect)

        # Soft top/bottom vignette overlay for depth
        vignette = QLinearGradient(card_rect.topLeft(), card_rect.bottomLeft())
        vignette.setColorAt(0.0, QColor(0, 0, 0, 15))
        vignette.setColorAt(0.75, QColor(0, 0, 0, 0))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 110))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(vignette))
        painter.drawRect(card_rect)

        painter.restore()

        # Elegant border around the 3D card
        border_color = QColor(237, 137, 54, 200) if self.is_playing else QColor(226, 232, 240, 220)
        painter.setPen(QPen(border_color, 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(card_rect, 20, 20)

    def _draw_face_animation_overlay(self, painter: QPainter, card_rect: QRectF):
        """
        Draw responsive facial animations:
        - Natural eye blinking
        - Audio-driven mouth cavity and lip-sync
        """
        w = card_rect.width()
        h = card_rect.height()
        cx = card_rect.left() + w * 0.498

        # 1. Animated Eyelid Blinking
        # Eye locations in the normalized card space:
        # Left eye: (cx - w * 0.075, card_rect.top() + h * 0.33)
        # Right eye: (cx + w * 0.082, card_rect.top() + h * 0.33)
        if self.blink_progress > 0.02:
            lid_color = QColor(224, 168, 136)  # Warm skin tone matching 3D model
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(lid_color))

            eye_y = card_rect.top() + h * 0.332
            eye_w = w * 0.09
            eye_h = h * 0.058 * self.blink_progress

            for ex in [cx - w * 0.080, cx + w * 0.084]:
                painter.drawEllipse(QPointF(ex, eye_y), eye_w * 0.5, eye_h)

        # 2. Dynamic Lip-Sync Mouth
        # Mouth center in normalized card space:
        # Located around (cx + 2, card_rect.top() + h * 0.495)
        mouth_cx = cx + 1.0
        mouth_cy = card_rect.top() + h * 0.492

        openness = self.openness if self.is_playing else 0.0

        if openness > 0.08:
            # Active speech - draw dynamic mouth cavity
            half_w = (w * 0.085) * (0.65 + self.width_factor * 0.7)
            open_h = max(3.0, openness * (h * 0.085))

            top_y = mouth_cy - (open_h * 0.3)
            bot_y = mouth_cy + (open_h * 0.7)

            # Mouth cavity path
            mouth_path = QPainterPath()
            mouth_path.moveTo(mouth_cx - half_w, mouth_cy)
            mouth_path.quadTo(mouth_cx, top_y, mouth_cx + half_w, mouth_cy)
            mouth_path.quadTo(mouth_cx, bot_y, mouth_cx - half_w, mouth_cy)

            # Draw deep inner mouth cavity
            painter.setPen(QPen(QColor(84, 18, 26), 1.5))
            painter.setBrush(QBrush(QColor(60, 10, 18)))
            painter.drawPath(mouth_path)

            # Upper teeth if mouth is open wide enough
            if self.viseme_type in ["EE", "AA"] and open_h > 5.0:
                painter.save()
                painter.setClipPath(mouth_path)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
                teeth_rect = QRectF(mouth_cx - half_w * 0.65, top_y - 1, half_w * 1.3, open_h * 0.42)
                painter.drawRoundedRect(teeth_rect, 2, 2)
                painter.restore()

            # Cute pink tongue
            painter.save()
            painter.setClipPath(mouth_path)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(230, 95, 100)))
            painter.drawEllipse(QPointF(mouth_cx, bot_y + 1), half_w * 0.55, open_h * 0.4)
            painter.restore()

    def _draw_status_badge(self, painter: QPainter, card_rect: QRectF):
        """Draw stylized pill status badge at the bottom of the card."""
        badge_w = card_rect.width() - 32
        badge_h = 28
        badge_x = card_rect.left() + 16
        badge_y = card_rect.bottom() - badge_h - 12
        badge_rect = QRectF(badge_x, badge_y, badge_w, badge_h)

        # Background pill with soft glassmorphic style
        painter.setPen(Qt.PenStyle.NoPen)
        if self.is_playing:
            painter.setBrush(QBrush(QColor(43, 108, 176, 210)))  # Deep friendly blue
            text = "✨ Papa Reading to You..."
            text_color = QColor(255, 255, 255)
        else:
            painter.setBrush(QBrush(QColor(26, 32, 44, 185)))   # Warm dark slate
            text = "📖 Ready to Listen"
            text_color = QColor(237, 242, 247)

        painter.drawRoundedRect(badge_rect, 14, 14)

        # Text
        painter.setPen(QPen(text_color))
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
