import os, sys, glob
import importlib
import time
import numpy as np

base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(base_path)

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from gym_cloud_sched_sim.envs.cloud_sched_sim_env import CloudSchedSimEnv

from_class = uic.loadUiType(os.path.join(base_path, 'gym_cloud_sched_sim', 'envs', 'gui_simulator', 'KubeSimGui.ui'))[0]

class KubeSimGui(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Cloud Scheduling Simulator')

        # Initialize rl related variables
        self.action = None
        self.nextAction = None
        self.state = np.zeros(12, dtype=np.float32)
        self.done = False
        self.info = None
        self.reward = 0
        self.reward_acc = 0

        # Initialize environment
        self.env = CloudSchedSimEnv()
        self.env.reset()

        # Fetch Scenarios from {base_path}/scenarios/
        self.scenarios_path = glob.glob(os.path.join(base_path, 'gym_cloud_sched_sim', 'envs', 'scenarios', '*.csv'))
        self.scenarios_fname = [os.path.basename(scenario_path) for scenario_path in self.scenarios_path]
        self.scenario_ComboBox.addItems(['Select Scenario', 'random'] + self.scenarios_fname)

        # Fetch reward functions from {base_path}/kube_rl_scheduler/strategies/reward/
        self.reward_functions_path = glob.glob(os.path.join(base_path, 'gym_cloud_sched_sim', 'envs', 'rewards', '*.py'))
        self.reward_functions_fname = [os.path.basename(reward_function_path) for reward_function_path in self.reward_functions_path]
        self.reward_function_ComboBox.addItems(['Select Reward Function'] + self.reward_functions_fname)

        # # Fetch rl models from {base_path}/kube_rl_scheduler/strategies/model/
        # self.rl_models_path = glob.glob(os.path.join(base_path, 'kube_rl_scheduler', 'strategies', 'model', '*.zip'))
        # self.rl_models_fname = [os.path.basename(model_path) for model_path in self.rl_models_path]
        # self.rl_model_ComboBox.addItems(['Select Model'] + self.rl_models_fname)

        # Fetch hr models from {base_path}/kube_hr_scheduler/model/
        self.hr_models_path = glob.glob(os.path.join(base_path, 'gym_cloud_sched_sim', 'envs', 'baselines', 'model', '*.py'))
        self.hr_models_fname = [os.path.basename(model_path) for model_path in self.hr_models_path]
        self.hr_model_ComboBox.addItems(['Select Model'] + self.hr_models_fname)
        # self.hr_model_ComboBox.addItems(['Select Model', 'test'])

        # # Fetch mm models from {base_path}/kube_mm_scheduler/model/
        # self.mm_models_path = glob.glob(os.path.join(base_path, 'kube_mm_scheduler', 'weight', '*.pt'))
        # self.mm_models_fname = [os.path.splitext(os.path.basename(model_path))[0] for model_path in self.mm_models_path]
        # self.mm_model_ComboBox.addItems(['Select Model'] + self.mm_models_fname)



        # Modules
        self.scenario = None
        self.reward_function = None
        # self.rl_model = None
        self.hr_model = None
        # self.mm_model = None
        self.model = None
        self.scheduler = None

        # Initialize visual status(Pending Pod)
        self.timeLabel.setText(str(0))
        self.pending_pod1 = None
        self.pending_pod2 = None
        self.pending_pod3 = None
        self.info_Area.setPlainText(f"scenario: {self.scenario} / strategy: {self.reward_function}")
        self.progressBar.setValue(0)
        self.progressBarLabel.setText(str(0) + '%')

        # Connect select buttons
        self.scenario_ComboBox.currentIndexChanged.connect(self.select_scenario)
        self.reward_function_ComboBox.currentIndexChanged.connect(self.select_reward_function)
        # self.rl_model_ComboBox.currentIndexChanged.connect(self.select_rl_model)
        self.hr_model_ComboBox.currentIndexChanged.connect(self.select_hr_model)
        # self.mm_model_ComboBox.currentIndexChanged.connect(self.select_mm_model)

        # Connect clickalbe buttons
        self.oneStepBtn.clicked.connect(self.btn_onestep)
        self.tenStepBtn.clicked.connect(self.btn_tenstep)
        self.resetBtn.clicked.connect(self.btn_reset)
        self.actionBtn_0.clicked.connect(lambda: self.btn_action(0))
        self.actionBtn_1.clicked.connect(lambda: self.btn_action(1))
        self.actionBtn_2.clicked.connect(lambda: self.btn_action(2))
        self.actionBtn_3.clicked.connect(lambda: self.btn_action(3))
        self.actionBtn_4.clicked.connect(lambda: self.btn_action(4))
        self.actionBtn_5.clicked.connect(lambda: self.btn_action(5))

        # Initialization function calls
        self.initialize_node_state()
        self.initialize_pod_state()
        self.update_lastAction()





    def select_scenario(self):
        self.scenario = self.scenario_ComboBox.currentText()
        if self.reward_function:
            self.init_env()
        if self.env.time != 0:
            self.btn_reset()
        
    def select_reward_function(self):
        self.reward_function = self.reward_function_ComboBox.currentText()
        if self.scenario:
            self.init_env()
        if self.env.time != 0:
            self.btn_reset()

    # def select_rl_model(self):
    #     if self.rl_model_ComboBox.currentIndex() == 0:
    #         return
    #     self.rl_model = self.rl_model_ComboBox.currentText()
    #     self.model = self.rl_model.split('.')[0] + "(RL)"
    #     scheduler_module_path = os.path.join('kube_rl_scheduler', 'scheduler', 'sim_rl_scheduler').replace('/', '.')
    #     scheduler_module = importlib.import_module(scheduler_module_path)
    #     self.scheduler = scheduler_module.SimRlScheduler(self.env, self.rl_model)
    #     self.update_all()
    #     self.hr_model = None
    #     self.hr_model_ComboBox.setCurrentIndex(0)
    #     self.mm_model = None
    #     self.mm_model_ComboBox.setCurrentIndex(0)
    #     if self.env.time != 0:
    #         self.btn_reset()

    def select_hr_model(self):
        if self.hr_model_ComboBox.currentIndex() == 0:
            return
        self.hr_model = self.hr_model_ComboBox.currentText()
        self.model = self.hr_model.split('.')[0] + "(HR)"
        scheduler_module_path = os.path.join('gym_cloud_sched_sim', 'envs', 'baselines', 'scheduler', 'baseline_scheduler').replace('/', '.')
        scheduler_module = importlib.import_module(scheduler_module_path)
        self.scheduler = scheduler_module.BaselineScheduler(self.env, self.hr_model)
        self.update_all()
        # self.rl_model = None
        # self.rl_model_ComboBox.setCurrentIndex(0)
        # self.mm_model = None
        # self.mm_model_ComboBox.setCurrentIndex(0)
        if self.env.time != 0:
            self.btn_reset()

    # def select_mm_model(self):
    #     if self.mm_model_ComboBox.currentIndex() == 0:
    #         return
    #     self.mm_model = self.mm_model_ComboBox.currentText()
    #     self.model = self.mm_model.split('.')[0] + "(MM)"
    #     scheduler_module_path = os.path.join('kube_mm_scheduler', 'scheduler', 'sim_mm_scheduler').replace('/', '.')
    #     scheduler_module = importlib.import_module(scheduler_module_path)
    #     self.scheduler = scheduler_module.SimMmScheduler(self.mm_model)
    #     self.update_all()
    #     self.rl_model = None
    #     self.rl_model_ComboBox.setCurrentIndex(0)
    #     self.hr_model = None
    #     self.hr_model_ComboBox.setCurrentIndex(0)
    #     if self.env.time != 0:
    #         self.btn_reset()

    def btn_onestep(self):
        if not self.scheduler or not self.scenario or not self.reward_function or not self.env:
            print("Initialize all modules first")
            return
        self.action = self.nextAction
        self.state, self.reward, self.done, self.info = self.env.step(self.action)
        # If just started, do not update reward_acc
        if self.env.time != 0:
            self.reward_acc += self.reward
        self.update_all()

    def btn_tenstep(self):
        if not self.scheduler or not self.scenario or not self.reward_function or not self.env:
            print("Initialize all modules first")
            return
        for _ in range(10):
            self.action = self.nextAction
            self.state, self.reward, self.done, self.info = self.env.step(self.action)
            self.reward_acc += self.reward
            self.update_all()
            if self.done:
                break
        self.update_all()

    def btn_reset(self):
        self.env.reset()
        self.reward = 0
        self.reward_acc = 0
        self.state = np.zeros(12, dtype=np.float32)
        self.action = None
        self.nextAction = None
        self.done = False
        self.info = None
        self.reward = 0
        self.update_all()

    def btn_action(self, action):
        if not self.scenario or not self.reward_function or not self.env:
            print("Initialize all modules first")
            return
        self.action = action
        self.state, self.reward, self.done, self.info = self.env.step(self.action)
        self.reward_acc += self.reward
        self.update_all()

    def init_env(self):
        if not self.reward_function or not self.scenario:
            return
        self.env = CloudSchedSimEnv(self.reward_function, self.scenario)
        self.state = self.env.reset()
        self.action = None
        self.nextAction = None
        self.done = False
        self.info = None
        self.reward = 0
        self.reward_acc = 0
        self.update_all()






    # ============= Initialize functions =============
    def initialize_node_state(self):
        self.node1_cpu_bar.setValue(0)
        self.node1_mem_bar.setValue(0)
        self.node2_cpu_bar.setValue(0)
        self.node2_mem_bar.setValue(0)
        self.node3_cpu_bar.setValue(0)
        self.node3_mem_bar.setValue(0)
        self.node4_cpu_bar.setValue(0)
        self.node4_mem_bar.setValue(0)
        self.node5_cpu_bar.setValue(0)
        self.node5_mem_bar.setValue(0)

    def initialize_pod_state(self, scope=0): # 0: All
        if scope == 1 or scope == 0:
            # Pod 1
            self.pod1_idx.setText('')
            self.pod1_cpu_req.setText('')
            self.pod1_mem_req.setText('')
            self.pod1_duration.setText('')
            self.pod1_arrival_t.setText('')
        if scope == 2 or scope == 0:
            # Pod 2
            self.pod2_idx.setText('')
            self.pod2_cpu_req.setText('')
            self.pod2_mem_req.setText('')
            self.pod2_duration.setText('')
            self.pod2_arrival_t.setText('')
        if scope == 3 or scope == 0:
            # Pod 3
            self.pod3_idx.setText('')
            self.pod3_cpu_req.setText('')
            self.pod3_mem_req.setText('')
            self.pod3_duration.setText('')
            self.pod3_arrival_t.setText('')


    # ============= Update functions =============
    def update_node_state(self):
        self.node2_cpu_bar.setValue(int(self.env.cluster.nodes[1].status['cpu_ratio'] * 100))
        self.node1_cpu_bar.setValue(int(self.env.cluster.nodes[0].status['cpu_ratio'] * 100))
        self.node1_mem_bar.setValue(int(self.env.cluster.nodes[0].status['mem_ratio'] * 100))
        self.node2_mem_bar.setValue(int(self.env.cluster.nodes[1].status['mem_ratio'] * 100))
        self.node3_cpu_bar.setValue(int(self.env.cluster.nodes[2].status['cpu_ratio'] * 100))
        self.node3_mem_bar.setValue(int(self.env.cluster.nodes[2].status['mem_ratio'] * 100))
        self.node4_cpu_bar.setValue(int(self.env.cluster.nodes[3].status['cpu_ratio'] * 100))
        self.node4_mem_bar.setValue(int(self.env.cluster.nodes[3].status['mem_ratio'] * 100))
        self.node5_cpu_bar.setValue(int(self.env.cluster.nodes[4].status['cpu_ratio'] * 100))
        self.node5_mem_bar.setValue(int(self.env.cluster.nodes[4].status['mem_ratio'] * 100))

    def update_pod_state(self):
        # Pod 1
        if len(self.env.cluster.pending_pods) > 0:
            self.pending_pod1 = self.env.cluster.pending_pods[0]
            self.pod1_idx.setText(f"{self.pending_pod1.pod_idx}th")
            self.pod1_cpu_req.setText(f"{self.pending_pod1.spec['cpu_req']}m ({round(self.pending_pod1.spec['cpu_ratio'] * 100, 2)}%)")
            self.pod1_mem_req.setText(f"{self.pending_pod1.spec['mem_req']}Mi ({round(self.pending_pod1.spec['mem_ratio'] * 100, 2)}%)")
            self.pod1_duration.setText(f"{self.pending_pod1.spec['duration']}m")
            self.pod1_arrival_t.setText(f"{self.pending_pod1.spec['arrival_time']}s")
        else:
            self.initialize_pod_state(1)
        # Pod 2
        if len(self.env.cluster.pending_pods) > 1:
            self.pending_pod2 = self.env.cluster.pending_pods[1]
            self.pod2_idx.setText(f"{self.pending_pod2.pod_idx}th")
            self.pod2_cpu_req.setText(f"{self.pending_pod2.spec['cpu_req']}m ({int(self.pending_pod2.spec['cpu_ratio'] * 100)}%)")
            self.pod2_mem_req.setText(f"{self.pending_pod2.spec['mem_req']}Mi ({int(self.pending_pod2.spec['mem_ratio'] * 100)}%)")
            self.pod2_duration.setText(f"{self.pending_pod2.spec['duration']}m")
            self.pod2_arrival_t.setText(f"{self.pending_pod2.spec['arrival_time']}s")
        else:
            self.initialize_pod_state(2)
        # Pod 3
        if len(self.env.cluster.pending_pods) > 2:
            self.pending_pod3 = self.env.cluster.pending_pods[2]
            self.pod3_idx.setText(f"{self.pending_pod3.pod_idx}th")
            self.pod3_cpu_req.setText(f"{self.pending_pod3.spec['cpu_req']}m ({int(self.pending_pod3.spec['cpu_ratio'] * 100)}%)")
            self.pod3_mem_req.setText(f"{self.pending_pod3.spec['mem_req']}Mi ({int(self.pending_pod3.spec['mem_ratio'] * 100)}%)")
            self.pod3_duration.setText(f"{self.pending_pod3.spec['duration']}m")
            self.pod3_arrival_t.setText(f"{self.pending_pod3.spec['arrival_time']}s")
        else:
            self.initialize_pod_state(3)

    def update_settings(self):
        settings = f"scenario:\n{self.scenario}\nreward:\n{self.reward_function}\nmodel:\n{self.model}"
        self.settings_Area.setPlainText(settings)

    def update_info(self):
        text = f"""state: {self.env.get_state()}\naction: {self.action}\nreward: {round(self.env.reward, 2)}\nreward(acc): {round(self.reward_acc, 2)}\ndone: {self.env.get_done()}\nis_scheduled: {self.info['is_scheduled'] if self.info is not None else "False"}"""
        self.info_Area.setPlainText(text)

    def update_progressBar(self):
        if self.scenario == 'random':
            len_scenario = 1000
            len_scheduled = len(self.env.cluster.terminated_pods + self.env.cluster.running_pods)
        else:
            len_scenario = len(self.env.stress_gen.scenario)
            len_scheduled = len(self.env.cluster.terminated_pods + self.env.cluster.running_pods)
        progress = int(len_scheduled / len_scenario * 100)
        self.progressBar.setValue(progress)
        self.progressBarLabel.setText(f"{str(progress)}% ({len_scheduled}/{len_scenario})")

    def update_nextAction(self): 
        if not self.scheduler:
            return

        self.nextAction = self.scheduler.decision(self.env)
        self.nextAction_Area.setPlainText(str(self.nextAction))

    def update_lastAction(self, info=None):
        if self.action == None:
            lastAction = 'None'
        elif self.action == 0:
            lastAction = 'Stand by'
        elif self.action in  [1,2,3,4,5]:
            if info:
                if info['is_scheduled']:
                    pod = info['last_pod']
                    lastAction = f"Schedule {pod.pod_idx}th pod (cpu: {int(pod.spec['cpu_ratio']*100)}% / mem: {int(pod.spec['mem_ratio']*100)}%) to node {self.action}"
                else:
                    lastAction = f"Failed to schedule pod to node {self.action}"
        self.lastActionLabel.setText(lastAction)

    def update_time(self):
        time = self.env.time
        self.timeLabel.setText(str(time))

    def update_all(self):
        self.update_node_state()
        self.update_pod_state()
        self.update_settings()
        self.update_info()
        self.update_time()
        self.update_progressBar()
        self.update_nextAction()
        self.update_lastAction(self.info)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = KubeSimGui()
    myWindow.show()
    app.exec_()