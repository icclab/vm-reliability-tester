response_time_1 <- read.table("~/vm-reliability-tester/response_time_1.csv", sep=";", quote="\"")
response_time_2 <- read.table("~/vm-reliability-tester/response_time_2.csv", sep=";", quote="\"")
response_time_3 <- read.table("~/vm-reliability-tester/response_time_3.csv", sep=";", quote="\"")
response_time_4 <- read.table("~/vm-reliability-tester/response_time_4.csv", sep=";", quote="\"")
response_time_5 <- read.table("~/vm-reliability-tester/response_time_5.csv", sep=";", quote="\"")

test_run = response_time_1$V1

r_times1 = response_time_1$V2
r_times2 = response_time_2$V2
r_times3 = response_time_3$V2
r_times4 = response_time_4$V2
r_times5 = response_time_5$V2
mean(r_times1)
sd(r_times1)


test_run_name <- "Test.run"
r1_name <- "VM1"
r2_name <- "VM2"
r3_name <- "VM3"
r4_name <- "VM4"
r5_name <- "VM5"


df <- data.frame(test_run,
                      r_times1,
                      r_times2,
                      r_times3,
                      r_times4,
                      r_times5)
colnames(df) <- c(test_run_name,
                  r1_name,
                  r2_name,
                  r3_name,
                  r4_name,
                  r5_name)
print(df)
df$X <- rowMeans(data.frame(df$VM1,df$VM2,df$VM3,df$VM4,df$VM5))

range <- function(x){
  return(max(x) - min(x))
}

df$R <- apply(data.frame(df$VM1,df$VM2,df$VM3,df$VM4,df$VM5), 1, FUN=range)

R_bar = mean(df$R)

X_bar = mean(df$X)

D3 <- 0
D4 <- 2.114
A2 <- 0.577

LCL_r <- R_bar * D3
UCL_r <- R_bar * D4

LCL <- X_bar - A2 * R_bar
UCL <- X_bar + A2 * R_bar

failures_1 <- df[ df$VM1 > UCL, ]
failures_2 <- df[ df$VM2 > UCL, ]
failures_3 <- df[ df$VM3 > UCL, ]
failures_4 <- df[ df$VM4 > UCL, ]
failures_5 <- df[ df$VM5 > UCL, ]

n <- nrow (df)

num1 <- nrow(failures_1)
num2 <- nrow(failures_2)
num3 <- nrow(failures_3)
num4 <- nrow(failures_4)
num5 <- nrow(failures_5)

lambda1 <- num1 / n
lambda2 <- num2 / n
lambda3 <- num3 / n
lambda4 <- num4 / n
lambda5 <- num5 / n


