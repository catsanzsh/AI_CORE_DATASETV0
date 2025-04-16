 
This patch makes both PAL and NTSC use a 60 Hz VI timer and reports 60 Hz
as the default refresh rate, enabling a universal “60 FPS” mode.

diff --git a/src/r4300/r4300_core.c b/src/r4300/r4300_core.c
index abcdef1..abcdef2 100644
--- a/src/r4300/r4300_core.c
+++ b/src/r4300/r4300_core.c
@@ -97,13 +97,13 @@ static void init_vi_timer(void)
     /* Initialize the video‐interrupt timer */
     if (system_is_pal()) {
-        /* PAL normally fires VI every 33333 cycles (50 Hz) */
-        vi_period_cycles = R4300_CLK / 50;
+        /* PAL: force VI every ≈28658 cycles (60 Hz) */
+        vi_period_cycles = R4300_CLK / 60;
     } else {
-        /* NTSC normally fires VI every 28658 cycles (≈60.1 Hz) */
-        vi_period_cycles = R4300_CLK / 60;
+        /* NTSC: standard 60 Hz */
+        vi_period_cycles = R4300_CLK / 60;
     }
 
     /* Schedule first VI interrupt */
diff --git a/src/VI/vi_timing.h b/src/VI/vi_timing.h
index 1234567..7654321 100644
--- a/src/VI/vi_timing.h
+++ b/src/VI/vi_timing.h
@@ -7,7 +7,7 @@
  * Video interrupt timing constants
  */
 
-#define VI_REFRESH_DEFAULT  (system_is_pal() ? 50.0 : 60.0988)
+#define VI_REFRESH_DEFAULT  60.0    /* Always report 60 Hz */
