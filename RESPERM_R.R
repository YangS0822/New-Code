library(ggplot2)

setwd('/Users/yangshi/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据/New Code')
source('RESPERM_SOURCE.R')

setwd('/Users/yangshi/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据/实验一/Time_Series')
data = read.csv('Time_Series_40.csv')


### run RESPERM
sub_reg = res.perm(x = data$X, y = data$LR_Avg, N_perm = 1000)

#adding group
group = rep(NA, length(data$X))
group[0:sub_reg$k_star] = 1
group[-(0:sub_reg$k_star)] = 2

data$group = group


#split data
first = data[0:sub_reg$k_star,]
second = data[-(0:sub_reg$k_star),]

color_flag <- c('red', 'steel_blue')
### Plot in ggplot2
library(repr)
options(repr.plot.width = 10, repr.plot.height = 4)
fig = ggplot() + geom_point(data = data, aes(x = X, y = LR_Avg, color = group), show.legend = FALSE)+
  geom_smooth(data = first, aes(x = X, y = LR_Avg), formula = y~x, method = 'lm', color = 'grey39') + 
  geom_smooth(data = second, aes(x = X,y = LR_Avg), formula = y~x, method = 'lm', color = 'blue') 
fig

