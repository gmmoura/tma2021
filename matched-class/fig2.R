data<-read.csv(file='ccTLD-anycast-anycast.csv', sep=',' , h=T)

pdf(file='fig2.pdf', height=4, width=6)

plot(ecdf(data$combined2017),col='blue',main='', ylab='CDF', xlab='Combined Replicas',xlim=c(1,150), verticals=TRUE)
plot(ecdf(data$combined21),col='red',main='', ylab='CDF', xlab='Combined Replicas',xlim=c(1,150),add=T,, verticals=TRUE)
axis(side=1,at=c(0,25,50,75,100,125,150),labels=c("0","25","50","75","100","125","150"))
legend(70,0.4, legend=c("2017", "2021"), col=c("blue", "red"), lty=1:2, cex=1.2, box.lty=0)
dev.off()
