
library(igraph)

g <- static.power.law.game(50, 100,2,-1,FALSE,FALSE,TRUE)
degs <- sample(1:100, 100, replace=TRUE, prob=(1:100)^-2)
if (sum(degs) %% 2 != 0) { degs[1] <- degs[1] + 1 }
g5 <- degree.sequence.game(degs, method="vl")
all(degree(g5) == degs)
write.graph(g5,"graph.csv",format="edgelist")

G1 = graph.data.frame(read.csv("graph_den8.csv",header=TRUE), directed=FALSE)
pdf("graph_den8.pdf",width =10)

#par(mfcol=c(1,2))
split.screen( figs = c( 1, 2 ) )#screen 1,2
split.screen( figs = c( 1, 1 ), screen = 1 )#screen 3
split.screen( figs = c( 2, 1 ), screen = 2 )#screen 4,5

data = paste(" \n\n\n\n\n Graph-N(150)\nDENSITY:8")
screen(3)
layout1=layout.random(G1)
plot(G1, main = data, layout=layout1)
screen(4)
hist(degree(G1),col="dodgerblue",xlab="Degrees",ylab="Frequency", main="Histogram of Edge Degrees\n(Graph-N(150)")
dd = degree.distribution(G1,cumulative=TRUE)
screen(5)
plot(dd, log="xy", xlab="degree", ylab="cumulative frequency",main=" Edge Degree Distribution", col ="blue")

dev.off()

#degs <- sample(1:100, 100, replace=TRUE, prob=(1:100)^-2)
#if (sum(degs) %% 2 != 0) { degs[1] <- degs[1] + 1 }
#g5 <- degree.sequence.game(degs, method="vl")
#all(degree(g5) == degs)
#write.graph(g5,"graph_pl42.csv",format="edgelist")



