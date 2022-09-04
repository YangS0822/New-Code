setwd('/Users/mac/Library/CloudStorage/OneDrive-个人/毕业论文/Single_trial')
library(ggplot2)
source('RESPERM_SOURCE.R')

setwd('/Users/mac/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据')
#setwd('/Users/mac/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据/实验2数据/pre/Sub_01')
data = read.csv('Time_Series.csv', header = FALSE)
### run RESPERM
sub_reg = res.perm(x = data$V1, y = data$V2, N_perm = 1000)

#split data
first = data[0:sub_reg$k_star,]
second = data[-(0:sub_reg$k_star),]
group = rep(NA,length(data$V1))
group[0:sub_reg$k_star] = 1
group[-(0:sub_reg$k_star)] = 2
data$group = group

### Plot in ggplot2
fig = ggplot() + geom_point(data = data, aes(x = V1, y = V2, color = group))+
  geom_smooth(data = first, aes(x = V1, y = V2), formula = y~x, method = 'lm') + 
  geom_smooth(data = second, aes(x = V1,y = V2), formula = y~x, method = 'lm')



