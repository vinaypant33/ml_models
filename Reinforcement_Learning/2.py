import gym
import numpy as np



env = gym.make("MountainCar-v0", render_mode="human")  # add render_mode for new gym
state, info = env.reset()

learning_rate = 0.1 # The speed at which the algorithm learns and if the also learns fast it loses the information and if it is too slow it costs time 
discount  = 0.95  # Measurue how future rewards vs the current rewards 
EPISODES  = 25000 # The loop at whcih it takes to learn some times it takes less time but sometimes more time



# Get the details from the environment :  Get the high low and number of values for the environment.  
print(env.observation_space.high)
print(env.observation_space.low)
print(env.action_space.n)


# DISCRETE_OS_SIZE = [20 , 20] # This to be done
DISCRETE_OS_SIZE  = [20] * len(env.observation_space.high)
discrete_os_win_size  = (env.observation_space.high - env.observation_space.low) / DISCRETE_OS_SIZE

print(discrete_os_win_size)

q_table  = np.random.uniform(low = -2 , high = 0 , size=(DISCRETE_OS_SIZE + [env.action_space.n]))

# print(q_table.shape) # to check the shape of the combination

def get_discrete_state(state):
    discrete_state = (state - env.observation_space.low) / discrete_os_win_size
    return tuple(discrete_state.astype(np.int))


discrete_state = get_discrete_state(env.reset())

print(q_table[discrete_state])




# Combination for the qtable  :  check and confirm how can we do that : 



done = False
while not done:
    action = 2
    new_state, reward, terminated, truncated, info = env.step(action)
    print(reward , new_state)

    done = terminated or truncated
    env.render()

env.close()
