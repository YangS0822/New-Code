setwd('/Volumes/Media/毕业论文/实验一_分析/One_Third_split/evks_csv/Amp&Latency/Reformat_for_Scripts')
data = read.csv('N170_LAT_OTS_O1_R.csv')

library(ggpubr)
library(tidyverse)
library(rstatix)

## Visualization
data$PART = as.character(data$PART)

# Summary
Describe_Summary_data = data %>% group_by(PART, Condition, Hemisphere) %>% get_summary_stats(LAT, type = 'mean_sd')

bxp <- ggboxplot(data, x = 'Condition', y = 'LAT', color = 'PART')
bxp


## Check Assumptions - outliers: No EXTREME outliers
data %>% group_by(Hemisphere, Condition, PART) %>% identify_outliers(LAT)

## Check Assumptions - Normality: the data VIOLATED normality assumption
shapiro.test(data$LAT)


## 3-way ANOVA
res.aov <- anova_test(data = data, dv = LAT, wid = number, within = c(Hemisphere, PART, Condition), effect.size = 'pes')
get_anova_table(res.aov)

# if there is significant 3 way interactions : simple 2way interaction
two.way <- data %>% group_by(Condition) %>% anova_test(dv = LAT, wid = number, within = c(Hemisphere, PART), effect.size = 'pes')
get_anova_table(two.way)

## Simple Simple Main Effect
PART.effect <- data %>% group_by(Hemisphere, Condition) %>% anova_test(dv = AMP, wid = number, within = PART)
PART.effect



## Pairwise comparison - compute simple main effect: HEMISPHERE
Hemisphere.effect <- data %>% group_by(PART, Condition) %>% anova_test(dv = LAT, wid = number, within = Hemisphere) 



## T-test for Hemisphere
data %>% group_by(Condition) %>% pairwise_t_test(AMP ~ Hemisphere, paired = TRUE, p.adjust.method = 'bonferroni')
pairwise_t_test(data,AMP ~ Hemisphere, paired = TRUE, p.adjust.method = 'bonferroni')

## T - test for PART
data %>% group_by(Hemisphere,Condition) %>% pairwise_t_test(LAT ~ PART, paired = TRUE, p.adjust.method = 'bonferroni')
pairwise_t_test(data,AMP ~ PART, paired = TRUE, p.adjust.method = 'bonferroni')



#### Visualization of ANOVA RESULTS
pwc <- pwc %>% add_xy_position(x = 'Condition')
pwc.filtered <- pwc %>% filter(PART == '1', Hemisphere == 'Left')

bxp + stat_pvalue_manual(pwc.filtered, tip.length = 0, hide.ns = TRUE) + labs(subtitle = get_test_label(res.aov, detailed = TRUE), caption = get_pwc_label((pwc)))



