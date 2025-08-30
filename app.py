import streamlit as st
import pandas as pd

# ---------- Scheduling Algorithms ---------- #

def fcfs(n, arrival, burst):
    process = list(range(1, n+1))
    current = 0
    rows = []
    for i in range(n):
        if current < arrival[i]:
            current = arrival[i]
        ct = current + burst[i]
        tat = ct - arrival[i]
        wt = tat - burst[i]
        rows.append([process[i], arrival[i], burst[i], ct, tat, wt])
        current = ct
    df = pd.DataFrame(rows, columns=["PID","AT","BT","CT","TAT","WT"])
    return df

def sjf(n, arrival, burst):
    process = list(range(1, n+1))
    completed = 0
    current = 0
    done = [False]*n
    rows = []
    while completed < n:
        ready = [i for i in range(n) if not done[i] and arrival[i] <= current]
        if not ready:
            current += 1
            continue
        ready.sort(key=lambda x: (burst[x], arrival[x], x))
        idx = ready[0]
        ct = current + burst[idx]
        tat = ct - arrival[idx]
        wt = tat - burst[idx]
        rows.append([process[idx], arrival[idx], burst[idx], ct, tat, wt])
        done[idx] = True
        completed += 1
        current = ct
    df = pd.DataFrame(rows, columns=["PID","AT","BT","CT","TAT","WT"])
    return df

def srtf(n, arrival, burst):
    process = list(range(1, n+1))
    remaining = burst[:]
    current = 0
    completed = 0
    done = [False]*n
    rows = []
    while completed < n:
        ready = [i for i in range(n) if not done[i] and arrival[i] <= current and remaining[i] > 0]
        if not ready:
            current += 1
            continue
        ready.sort(key=lambda x: (remaining[x], arrival[x], x))
        idx = ready[0]
        remaining[idx] -= 1
        current += 1
        if remaining[idx] == 0:
            ct = current
            tat = ct - arrival[idx]
            wt = tat - burst[idx]
            rows.append([process[idx], arrival[idx], burst[idx], ct, tat, wt])
            done[idx] = True
            completed += 1
    df = pd.DataFrame(rows, columns=["PID","AT","BT","CT","TAT","WT"])
    return df

def round_robin(n, arrival, burst, q):
    process = list(range(1, n+1))
    remaining = burst[:]
    ct = [0]*n
    tat = [0]*n
    wt = [0]*n
    rt = [-1]*n
    current = 0
    completed = 0
    ready = []
    rows = []
    while completed < n:
        for i in range(n):
            if arrival[i] <= current and remaining[i] > 0 and i not in ready:
                ready.append(i)
        if not ready:
            current += 1
            continue
        idx = ready.pop(0)
        if rt[idx] == -1:
            rt[idx] = current - arrival[idx]
        time = min(q, remaining[idx])
        remaining[idx] -= time
        current += time
        for j in range(n):
            if arrival[j] <= current and remaining[j] > 0 and j not in ready:
                ready.append(j)
        if remaining[idx] == 0:
            ct[idx] = current
            tat[idx] = ct[idx] - arrival[idx]
            wt[idx] = tat[idx] - burst[idx]
            rows.append([process[idx], arrival[idx], burst[idx], ct[idx], tat[idx], wt[idx], rt[idx]])
            completed += 1
        else:
            ready.append(idx)
    df = pd.DataFrame(rows, columns=["PID","AT","BT","CT","TAT","WT","RT"])
    return df

def priority_np(n, arrival, burst, priority, higher_number_higher_priority=True):
    process = list(range(1, n+1))
    done = [False]*n
    current = 0
    completed = 0
    rows = []
    while completed < n:
        ready = [i for i in range(n) if not done[i] and arrival[i] <= current]
        if not ready:
            current += 1
            continue
        if higher_number_higher_priority:
            ready.sort(key=lambda x: (-priority[x], arrival[x], burst[x], x))
        else:
            ready.sort(key=lambda x: (priority[x], arrival[x], burst[x], x))
        idx = ready[0]
        if current < arrival[idx]:
            current = arrival[idx]
        ct = current + burst[idx]
        tat = ct - arrival[idx]
        wt = tat - burst[idx]
        rows.append([process[idx], arrival[idx], burst[idx], priority[idx], ct, tat, wt])
        done[idx] = True
        completed += 1
        current = ct
    df = pd.DataFrame(rows, columns=["PID","AT","BT","Priority","CT","TAT","WT"])
    return df

# ---------- Streamlit App ---------- #

st.title("CPU Scheduling Algorithms Simulator")

algo = st.selectbox("Select Scheduling Algorithm", 
                    ["FCFS", "SJF (Non-Preemptive)", "SRTF (Preemptive)", "Round Robin", "Priority (Non-Preemptive)"])

n = st.number_input("Number of Processes", min_value=1, step=1)

arrival_str = st.text_input("Enter Arrival Times (comma separated)")
burst_str = st.text_input("Enter Burst Times (comma separated)")

if arrival_str and burst_str:
    arrival = list(map(int, arrival_str.strip().split(",")))
    burst = list(map(int, burst_str.strip().split(",")))

    if len(arrival) != n or len(burst) != n:
        st.warning("⚠️ Please enter exactly N values for both arrival and burst times.")
    else:
        if algo == "FCFS":
            df = fcfs(n, arrival, burst)
        elif algo == "SJF (Non-Preemptive)":
            df = sjf(n, arrival, burst)
        elif algo == "SRTF (Preemptive)":
            df = srtf(n, arrival, burst)
        elif algo == "Round Robin":
            q = st.number_input("Enter Time Quantum", min_value=1, step=1)
            df = round_robin(n, arrival, burst, q)
        elif algo == "Priority (Non-Preemptive)":
            priority_str = st.text_input("Enter Priorities (comma separated)")
            if priority_str:
                priority = list(map(int, priority_str.strip().split(",")))
                if len(priority) != n:
                    st.warning("⚠️ Please enter exactly N values for priority.")
                    df = None
                else:
                    df = priority_np(n, arrival, burst, priority, higher_number_higher_priority=True)
            else:
                df = None
        else:
            df = None

        if df is not None:
            st.subheader("📊 Scheduling Results")
            st.dataframe(df)

            if "WT" in df.columns:
                st.write(f"**Average Waiting Time:** {round(df['WT'].mean(), 2)}")
            if "TAT" in df.columns:
                st.write(f"**Average Turnaround Time:** {round(df['TAT'].mean(), 2)}")
            if "RT" in df.columns:
                st.write(f"**Average Response Time:** {round(df['RT'].mean(), 2)}")

            length = df["CT"].max() - df["AT"].min()
            st.write(f"**Schedule Length:** {length}")
            st.write(f"**Throughput:** {round(n/length, 2)}")
