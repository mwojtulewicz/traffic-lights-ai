import matplotlib.pyplot as plt

def save_plots(mean_rewards, mean_throughput, mean_queue_len, prefix=''):
    plt.style.use('seaborn')

    plt.plot(mean_rewards)
    plt.xlabel('Episodes')
    plt.ylabel('Step reward mean')
    plt.savefig(f'./figures/{prefix}rewards.png')
    plt.close()

    plt.plot(mean_throughput)
    plt.xlabel('Episodes')
    plt.ylabel(f'Step throughput mean')
    plt.savefig(f'./figures/{prefix}throughputs.png')
    plt.close()

    plt.plot(mean_queue_len)
    plt.xlabel('Episodes')
    plt.ylabel(f'Step queue length mean')
    plt.savefig(f'./figures/{prefix}queue_lens.png')
    plt.close()