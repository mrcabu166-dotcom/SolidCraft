"""SolidCraft - 20-Slot Radial Slide Dryer Rotor Core
==================================================
Configurable parameter block (ประกาศไว้บนสุดของโค้ด CAD).
ทุกขนาดเป็น มม. / องศา  |  แกนหมุน = Z  |  ช่องที่ 1 อยู่ที่มุม 0 deg (แกน +X), เรียงทวนเข็มนาฬิกามองจากด้านบน
"""
import math

# ----------------------------------------------------------------------------
# 0. SHAFT / MOTOR COUPLING  (ปรับตามเพลาเครื่องปั่นจริงได้ทันที)
# ----------------------------------------------------------------------------
SHAFT_TYPE = "D_SHAFT"          # "D_SHAFT" | "HEX_COUPLING" | "THREADED_NUT"
SHAFT_DIAMETER = 8.0            # เส้นผ่านศูนย์กลางเพลา
SHAFT_CLEARANCE = 0.25          # รูจริง = SHAFT_DIAMETER + SHAFT_CLEARANCE
D_FLAT_DEPTH = 1.5              # ความลึกส่วนปาดเรียบของ D-shaft (ผิวโค้งถึงด้านเรียบ = 8 - 1.5 = 6.5)
SHAFT_BORE_DEPTH = 22.0         # ความลึกรูเสียบเพลา นับจากฐานแกน (Z=0)
SET_SCREW_DIA = 3.2             # รูสกรูตัวหนอน M3 (clearance)
CAPTIVE_NUT_WIDTH = 5.6         # ช่องนอต M3 : กว้าง (ข้างหกเหลี่ยม)
CAPTIVE_NUT_THICKNESS = 2.6     # ช่องนอต M3 : หนา (ตามแนวสกรู)
BOTTOM_SKIRT_CLEARANCE = 5.0    # ระยะยกขอบฐานดุมหลบซีลยาง/เบ้าลูกปืนของโถปั่น

# THREADED_NUT mode : นอตเหล็กฝัง (ค่าเริ่มต้น M8)
NUT_AF = 13.0                   # ระยะข้างหกเหลี่ยมของนอต M8
NUT_THICK = 6.5                 # ความหนานอต M8
NUT_POCKET_CLEAR = 0.25         # เผื่อช่องนอต

# ----------------------------------------------------------------------------
# 1. SLIDE & 20-SLOT CORE
# ----------------------------------------------------------------------------
SLIDE_W = 25.4                  # กว้าง (ตามแนวรัศมี)
SLIDE_H = 75.0                  # สูง (แนวดิ่ง)
SLIDE_T = 1.2                   # หนา
N_SLOTS = 20
SLOT_PITCH = 360.0 / N_SLOTS    # 18 deg
SLOT_W = 1.6                    # ความกว้างร่องเสียบ
SLOT_END_CLEAR = 0.4            # เผื่อความยาวร่อง (ตามรัศมี) เหนือความกว้างสไลด์
R_HUB = 22.0                    # Inner Hub Radius = ปลายด้านในของร่อง (>= 20 ตามข้อกำหนด)
MIN_WALL_BETWEEN_SLOTS = 2.5    # ผนังกั้นระหว่างร่องด้านใน (ตรวจใน validate)

R_SLOT_OUT = R_HUB + SLIDE_W + SLOT_END_CLEAR       # ปลายด้านนอกของร่อง (47.8)
T_PLATE = 2.0                   # ความหนาผนังนำร่อง (plate) ข้างร่อง
T_END = 2.0                     # ความหนาผนังปิดปลายร่อง
R_END_OUT = R_SLOT_OUT + T_END
R_BASE = R_END_OUT + 2.2        # รัศมีจานฐาน
BASE_T = 12.0                   # ความหนาจานฐาน = ระดับรองสไลด์ (Z seat)
Z_SEAT = BASE_T
Z_SLIDE_TOP = Z_SEAT + SLIDE_H  # 87.0
PLATE_DROP = 1.0                # ผนังเตี้ยกว่าขอบบนสไลด์ (ให้สไลด์โผล่จับด้วยแหนบได้)
Z_CAGE_TOP = Z_SLIDE_TOP - PLATE_DROP
R_HUB_FILL = 28.0               # ดุมตัน (ปิดช่องแคบระหว่างผนังด้านใน)
RING_GAP = 0.2                  # ระยะห่างแหวนล็อก - ขอบบนสไลด์
Z_HUB_TOP = Z_SLIDE_TOP + RING_GAP   # 87.2 = ระนาบที่แหวนล็อกนั่ง

# ฐานรองสไลด์ + รูระบาย
DRAIN_W = 3.0                   # ร่องระบายรายช่อง กว้าง
DRAIN_H = 4.0                   # ร่องระบายรายช่อง สูง (ปลายแหลม 45 deg)
WEEP_LEN = 4.0                  # ความยาวหน้าต่างระบายทะลุพื้นร่อง (ตามรัศมี)
WEEP_X = [(27.0, 31.0), (35.0, 39.0), (43.0, R_SLOT_OUT)]   # ช่วงรัศมีของหน้าต่าง (ระหว่างนั้นเป็นคานรองสไลด์)
SLIDE_INNER_CLEAR = 0.2         # ระยะสไลด์ถึงปลายร่องด้านใน (ใช้ใน assembly)

# บอสเพลา + ร่องหลบซีล
R_BOSS = 14.0                   # บอสทรงกระบอกหนา
RELIEF_FLAT = 0.0               # ความกว้างหลังคาแบนของร่องหลบซีล (0 = ลาด 45 deg ล้วน -> Zero Support ; >0 ต้อง bridge)
R_RELIEF_OUT = None             # คำนวณด้านล่าง
BORE_LEADIN = 1.0               # Lead-in chamfer 1.0 x 45
Z_SET_SCREW = 16.0              # ความสูงแกนสกรูล็อกเพลา
SET_SCREW_ANGLE = SLOT_PITCH / 2.0   # 9 deg : อยู่กลางร่องระหว่างช่อง 1 และ 2
NUT_WALL = 2.0                  # เนื้อพลาสติกระหว่างด้านเรียบเพลากับช่องนอต

# ----------------------------------------------------------------------------
# 2. BAYONET + COMB RING
# ----------------------------------------------------------------------------
N_BAYONET = 4                   # 2 หรือ 4 ตำแหน่ง สมมาตร
BAYONET_TWIST = 10.0            # บิดล็อก (deg) : 10-15 ; 10 ทำให้ซี่หวีหลบสไลด์ทุกแผ่นตอนปลดล็อก
BAYONET_CLEARANCE = 0.30        # Clearance ร่องล็อก
R_POST = 14.0                   # แกนรับล็อกด้านบน
POST_TOP_ABOVE_RING = 2.0
RING_T = 4.0                    # ความหนาแหวน (หน้าเรียบสองด้าน)
R_RING_BORE = R_POST + BAYONET_CLEARANCE
LUG_W = 2.4
LUG_H = 2.4
LUG_PROJ = 2.0
R_GROOVE_FLOOR = R_RING_BORE - LUG_PROJ - BAYONET_CLEARANCE   # 12.0
Z_POST_TOP = Z_HUB_TOP + RING_T + POST_TOP_ABOVE_RING
R_RING_BODY = 36.0
TOOTH_W = 4.0
R_TOOTH_OUT = R_HUB + SLIDE_W   # 47.4 (ปลายซี่คลุมขอบบนสไลด์ถึงปลายนอก)
R_TOOTH_IN = R_RING_BODY - 2.0

# ----------------------------------------------------------------------------
# 3. BALANCE MARKS
# ----------------------------------------------------------------------------
NUM_DEBOSS = 0.8                # ตัวเลขปั๊มจม ลึก 0.8
NUM_FONT = 7.0                  # ~ตัวเลขสูง 5.1 มม.
NUM_FONT_NAME = "Arial"
R_NUM_RING = 29.0               # รัศมีวางตัวเลขบนแหวน
Z_NUM_RIM = 7.5                 # ความสูงกึ่งกลางตัวเลขบนขอบฐาน
NOTCH_W = 2.4
NOTCH_D = 1.2

# ----------------------------------------------------------------------------
# 4. EXPORT / OUTPUT
# ----------------------------------------------------------------------------
STL_LINEAR_DEFLECTION = 0.01    # mm
STL_ANGULAR_DEG = 0.1           # deg
STL_ANGULAR_RAD = math.radians(STL_ANGULAR_DEG)
SMALL_FACE_AREA = 200.0         # mm2 : หน้าโค้งเล็ก (กรวย lead-in, เพดานรูเพลา, รูสกรู) ใช้ angular หยาบกว่า
SMALL_FACE_ANGULAR_DEG = 5.0    # (linear 0.01 mm ยังใช้กับทุกหน้า -> ความคลาดทางเรขาคณิต <= 0.01 mm เท่ากัน)
GLYPH_ANGULAR_DEG = 10.0        # ผนังตัวเลข 0.8 mm : OCCT mesh แบบ grid 2 ทิศ -> 0.1 deg ทำให้ไฟล์เป็น GB; linear 0.01 ยังคงเดิม

# derived
R_RELIEF_OUT = R_BOSS + BOTTOM_SKIRT_CLEARANCE + RELIEF_FLAT   # รัศมีนอกของร่องหลบซีล (19.0)
GLYPH_SAG = 0.003               # mm : ความคลาดของตัวเลขแบบ polyline (ใช้กับ STL เท่านั้น)
CONE_TIP_R = 0.5                # ตัดยอดกรวยเพดานรูเพลา (กัน apex เสียใน mesh)
SHAFT_HOLE_D = SHAFT_DIAMETER + SHAFT_CLEARANCE
D_FLAT_U = SHAFT_DIAMETER / 2.0 - D_FLAT_DEPTH + SHAFT_CLEARANCE / 2.0   # ตำแหน่งด้านเรียบในรู (2.625)


def slot_angle(k):
    """มุมศูนย์กลางของช่องที่ k (k = 0..19  <->  ช่องที่ 1..20)"""
    return k * SLOT_PITCH


def pair_label(k):
    """เลขจับคู่ตรงข้าม 180 deg : ช่อง k และ k+10 ใช้เลขเดียวกัน (1..10)"""
    return (k % (N_SLOTS // 2)) + 1
