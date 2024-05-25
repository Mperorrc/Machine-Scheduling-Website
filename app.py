from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd

app = Flask(__name__)

@app.route('/')

def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    if request.method == 'POST':
        data = request.get_json()

        num_machines = int(data['num_machines'])
        num_jobs = int(data['num_jobs'])
        num_operations = int(data['num_operations'])
        jom_mat = data['jom_mat']
        machine_mat = data['machine_mat']
        minimization_criteria = int(data['minimization_criteria'])
        due_dates = data['due_dates']
        arrival_dates = data['arrival_dates']
        num_constraints = data['num_constraints']
        constraints = data['constraints']
        penalty_costs = data['penalty_costs']

        for i in range(num_jobs):
            due_dates[i] = int(due_dates[i])
            arrival_dates[i] = int(arrival_dates[i])
            penalty_costs[i] = int(penalty_costs[i])
            for j in range(num_operations):
                    jom_mat[i][j][0] = int(jom_mat[i][j][0])
                    jom_mat[i][j][1] = int(jom_mat[i][j][1])

        for i in range(num_jobs):
            for j in range(num_operations):
                    jom_mat[i][j][0]-=1

        for i in range(num_machines):
             machine_mat[i][0]=int(machine_mat[i][0])
             machine_mat[i][1]=int(machine_mat[i][1])
             machine_mat[i][2]=int(machine_mat[i][2])
             machine_mat[i][3]=int(machine_mat[i][3])
        jom_mat = np.array(jom_mat)
        machine_mat = np.array(machine_mat)
        due_dates = np.array(due_dates)
        arrival_dates = np.array(arrival_dates)
        
        idle_times = [0]*(num_machines)
        running_energy_costs = [0]*num_machines
        waiting_energy_costs = [0]*num_machines
        scheduled_jobs = []
        total_energy_costs = [0]*num_jobs
        total_costs = 0
        penalty_cost = 0
        
        if minimization_criteria==1:
            # TARDY TIME
            indices = np.zeros(num_jobs)
            running_indices = num_jobs
            prev_finish_time = arrival_dates
            relative_due_dates = due_dates - min(due_dates)
            machine_free_time = []

            for i in range(num_machines):
                machine_free_time.append([0]*machine_mat[i][0])

            while running_indices:
                running_indices = 0
                next_index = 0
                least_time = float('inf')
                for i in range(num_jobs):
                    if (indices[i]<num_operations and jom_mat[i][int(indices[i])][0]>=0):
                        running_indices += 1
                        new_tardy_time = prev_finish_time[i]+jom_mat[i][int(indices[i])][1] -relative_due_dates[i]
                        if (new_tardy_time<least_time):
                            least_time = new_tardy_time
                            next_index = i
                        elif (new_tardy_time==least_time and jom_mat[i][int(indices[i])][1]<jom_mat[i][int(indices[next_index])][1]):
                            next_index = i
                        
                if running_indices ==0:
                    break
                new_finish_time = jom_mat[next_index][int(indices[next_index])][1] + max(machine_free_time[jom_mat[next_index][int(indices[next_index])][0]][0],prev_finish_time[next_index])
                prev_time = max(machine_free_time[jom_mat[next_index][int(indices[next_index])][0]][0],prev_finish_time[next_index])
                scheduled_jobs.append([next_index,int(indices[next_index]),prev_time,new_finish_time])

                idle_times[jom_mat[next_index][int(indices[next_index])][0]] += max(0,prev_finish_time[next_index] - machine_free_time[jom_mat[next_index][int(indices[next_index])][0]][0])
                running_energy_costs[jom_mat[next_index][int(indices[next_index])][0]] += jom_mat[next_index][int(indices[next_index])][1]*machine_mat[jom_mat[next_index][int(indices[next_index])][0]][1]
                waiting_energy_costs[jom_mat[next_index][int(indices[next_index])][0]] = idle_times[jom_mat[next_index][int(indices[next_index])][0]]*machine_mat[jom_mat[next_index][int(indices[next_index])][0]][3]
                prev_finish_time[next_index] = new_finish_time
                machine_free_time[jom_mat[next_index][int(indices[next_index])][0]][0] = new_finish_time
                machine_free_time[jom_mat[next_index][int(indices[next_index])][0]] = sorted(machine_free_time[jom_mat[next_index][int(indices[next_index])][0]])
                indices[next_index]+=1
            
            
            
            for i in range(num_machines):
                total_energy_costs[i] += machine_mat[i][2]+running_energy_costs[i]+waiting_energy_costs[i]
                total_costs+=machine_mat[i][2]+running_energy_costs[i]+waiting_energy_costs[i]
            
            for i in range(num_jobs):
                penalty_cost += max(0,prev_finish_time[i]-due_dates[i])*penalty_costs[i]
            
            total_costs+=penalty_cost
            print(scheduled_jobs)
        
        flatten_scheduled_jobs = [item for sublist in scheduled_jobs for item in sublist]
        scheduled_jobs = [int(item) for item in flatten_scheduled_jobs]
        running_energy_costs = [int(item) for item in running_energy_costs]
        waiting_energy_costs = [int(item) for item in waiting_energy_costs]
        total_energy_costs = [int(item) for item in total_energy_costs]
        idle_times = [int(item) for item in idle_times]
        total_costs = str(total_costs)
        penalty_cost = str(penalty_cost)

        return jsonify({
             'scheduled_jobs' : scheduled_jobs,
             'running_energy_costs' : running_energy_costs,
             'waiting_energy_costs' : waiting_energy_costs,
             'total_energy_costs' : total_energy_costs,
             'total_costs' : total_costs,
             'idle_times' : idle_times,
             'penalty_costs':penalty_cost
             })

if __name__ == "__main__":
    app.run(debug=True)
