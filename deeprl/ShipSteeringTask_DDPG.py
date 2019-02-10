import numpy as np
import tensorflow as tf
from agents.ddpg import *
from matplotlib import pyplot as plt
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['text.usetex'] = True

ENV_NAME = "ShipSteeringEnv-v0"

env = ContinuousWrapper(gym.make(ENV_NAME))
action_dim = env.action_space.shape[0]
state_dim = env.observation_space.shape
critic = CriticNetwork(action_dim=action_dim, state_dim= state_dim)
actor = ActorNetwork(action_dim=action_dim, state_dim= state_dim)
memory = Memory(100000, state_dim, 1, 64)

with tf.Session() as sess:
    agent = DDPG(sess, actor, critic, memory, env=env, max_test_epoch=3000,warm_up=50000,record=False,max_step_per_game = 3000,stop_when_reach=True,is_plot=True,
                 render=False, max_step=5000000, env_name=ENV_NAME,noise_theta=0.15,noise_sigma=1.0)
    agent.train()


    agent.evaluate()
    #
    # agent.restore()
    # # Draw plot
    # plt.style.use('bmh')
    # plt.ion()
    #
    # plt.figure(1)
    # cummulated_reward = []
    # plt.plot([850, 850], [880, 920], 'k', linewidth=2.0)
    # plt.plot([950, 950], [880, 920], 'k', linewidth=2.0)
    # for epoch in range(100):
    #     state = env.reset()
    #     step = 0
    #     done = False
    #     epi_reward = 0
    #     while not done:
    #         state = state[np.newaxis]
    #         action = agent.action(state)
    #         state, reward, done, _ = env.step(action.flatten())
    #         step += 1
    #         epi_reward += reward
    #
    #         if (step > 3000): done = True
    #
    #     cummulated_reward.append(epi_reward)
    #     plt.plot(env.env.get_xhist(), env.env.get_yhist(), linewidth=0.5)
    #     # plt.axis('equal')
    #     plt.ylim([0, 1000])
    #     plt.xlim([0, 1000])
    #     plt.xlabel('Distances (m)')
    #     plt.ylabel('Distances (m)')
    #
    # agent.save_plot_figure(plt, 'evaluate_trajectory.pdf')

    # plt.show()

    # total_reward = agent.restore_plot_data("total_reward.npy")
    # total_step = agent.restore_plot_data("total_step.npy")
    # xhist = agent.restore_plot_data("x_hist.npy")
    # yhist = agent.restore_plot_data("y_hist.npy")
    #
    # plt.style.use('bmh')
    # plt.figure(1)
    # plt.xlabel('Distances (m)')
    # plt.ylabel('Distances (m)')
    # plt.ylim([0, 1000])
    # plt.xlim([0, 1000])
    # for episode in range(xhist.shape[0]):
    #     plt.plot(xhist[episode,], yhist[episode,], linewidth=0.5, label='trajectory')
    # # plt.legend()
    # agent.save_plot_figure(plt, 'train_trajectory.pdf')

    # plt.style.use('bmh')
    # plt.figure(2)
    # plt.xlabel('Episode')
    # plt.ylabel('Reward')
    #
    # xxx = total_reward.shape[0]
    # epis = np.arange(0, total_reward.shape[0], 1)
    # plt.plot(epis, total_reward, label='reward', linewidth=1.0)
    # # plt.ylim([args.ymin, args.ymax])
    # # plt.legend()
    # agent.save_plot_figure(plt, 'reward.pdf')
    #
    # plt.style.use('bmh')
    # plt.figure(3)
    # plt.xlabel('Episode')
    # plt.ylabel('Steps')
    # xxx = total_step.shape[0]
    # epis = np.arange(0, total_step.shape[0], 1)
    # plt.plot(epis, total_step, label='steps', linewidth=1.0)
    # # plt.ylim([args.ymin, args.ymax])
    # # plt.legend()
    # agent.save_plot_figure(plt, 'steps.pdf')