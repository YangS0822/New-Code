library(ggplot2)

setwd('/Users/yangshi/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据/New Code')
source('RESPERM_SOURCE.R')

setwd('/Users/yangshi/Library/CloudStorage/OneDrive-个人/毕业论文/实验数据/实验一/EEGs/Sub_040JoeFace')
data = read.csv('Time_Series.csv', header = FALSE)


### run RESPERM
sub_reg = res.perm(x = data$V1, y = data$V2, N_perm = 1000)

#adding group
group = rep(NA, length(data$V1))
group[0:sub_reg$k_star] = 1
group[-(0:sub_reg$k_star)] = 2

data$group = group


#split data
first = data[0:sub_reg$k_star,]
second = data[-(0:sub_reg$k_star),]


### Plot in ggplot2
library(repr)
options(repr.plot.width = 10, repr.plot.height = 4)
fig = ggplot() + geom_point(data = data, aes(x = V1, y = V2, color = group), show.legend = FALSE)+
  geom_smooth(data = first, aes(x = V1, y = V2), formula = y~x, method = 'lm') + 
  geom_smooth(data = second, aes(x = V1,y = V2), formula = y~x, method = 'lm')

fig

