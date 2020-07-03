
import json
import os
import torch
from mlagents.trainers.learn import run_cli, parse_command_line
from mlagents.trainers.settings import RunOptions
from mlagents.trainers.stats import StatsReporter
from mlagents.trainers.ppo.trainer import TestingConfiguration
from mlagents_envs.timers import _thread_timer_stacks


results = [("name", "steps", "use_torch", "num_torch_threads", "use_gpu" , "total", "tc_advance_total", "tc_advance_count", "update_total", "update_count", "evaluate_total", "evaluate_count")]

def run_experiment(name:str, steps:int, use_torch:bool, num_torch_threads:int, use_gpu:bool, config_name=None):
	TestingConfiguration.env_name = name
	TestingConfiguration.max_steps = steps
	TestingConfiguration.use_torch = use_torch
	TestingConfiguration.device = "cuda:0" if use_gpu else "cpu"
	if (not torch.cuda.is_available() and use_gpu) or (not use_torch and use_gpu):
		return name, steps, use_torch, num_torch_threads, use_gpu, "na","na","na","na","na","na","na"
	if config_name is None:
		config_name = name
	run_options = parse_command_line([f"config/ppo/{config_name}.yaml"])
	run_options.checkpoint_settings.run_id = f"{name}_test_" +str(steps) +"_"+("torch" if use_torch else "tf")
	run_options.checkpoint_settings.force = True
	for trainer_settings in run_options.behaviors.values():
		trainer_settings.threaded = False
	timers_path = os.path.join("results", run_options.checkpoint_settings.run_id, "run_logs", "timers.json")
	if use_torch:
		torch.set_num_threads(num_torch_threads)
	run_cli(run_options)
	StatsReporter.writers.clear()
	StatsReporter.stats_dict.clear()
	_thread_timer_stacks.clear()
	with open(timers_path) as timers_json_file:
		timers_json = json.load(timers_json_file)
		total = timers_json["total"]
		tc_advance = timers_json["children"]["TrainerController.start_learning"]["children"]["TrainerController.advance"]
		evaluate = timers_json["children"]["TrainerController.start_learning"]["children"]["TrainerController.advance"]["children"]["env_step"]["children"]["SubprocessEnvManager._take_step"]["children"]
		update = timers_json["children"]["TrainerController.start_learning"]["children"]["TrainerController.advance"]["children"]["trainer_advance"]["children"]["_update_policy"]["children"]
		tc_advance_total = tc_advance["total"]
		tc_advance_count = tc_advance["count"]
	if use_torch:
		update_total = update["TorchPPOOptimizer.update"]["total"]
		evaluate_total = evaluate["TorchPolicy.evaluate"]["total"]
		update_count = update["TorchPPOOptimizer.update"]["count"]
		evaluate_count = evaluate["TorchPolicy.evaluate"]["count"]
	else:
		update_total = update["TFPPOOptimizer.update"]["total"]
		evaluate_total = evaluate["NNPolicy.evaluate"]["total"]
		update_count = update["TFPPOOptimizer.update"]["count"]
		evaluate_count= evaluate["NNPolicy.evaluate"]["count"]
	# todo: do total / count
	return name, steps, use_torch, num_torch_threads, use_gpu, total, tc_advance_total, tc_advance_count, update_total, update_count, evaluate_total, evaluate_count





results.append(run_experiment("3DBall", 20000, True, 4, True))
results.append(run_experiment("3DBall", 20000, True, 4, False))
# results.append(run_experiment("3DBall", 20000, True, 1, False))
# results.append(run_experiment("3DBall", 20000, False, None, False))

# results.append(run_experiment("GridWorld", 2000, True, 4, False))
# results.append(run_experiment("GridWorld", 2000, True, 1, False))
# results.append(run_experiment("GridWorld", 2000, False, None, False))

# results.append(run_experiment("PushBlock", 20000, True, 4, False))
# results.append(run_experiment("PushBlock", 20000, True, 1, False))
# results.append(run_experiment("PushBlock", 20000, False, None, False))

# results.append(run_experiment("Hallway", 20000, True, 4, False))
# results.append(run_experiment("Hallway", 20000, True, 1, False))
# results.append(run_experiment("Hallway", 20000, False, None, False))

# results.append(run_experiment("CrawlerStaticTarget", 50000, True, 4, False, "CrawlerStatic"))
# results.append(run_experiment("CrawlerStaticTarget", 50000, True, 1, False, "CrawlerStatic"))
# results.append(run_experiment("CrawlerStaticTarget", 50000, False, None, False, "CrawlerStatic"))


for r in results:
	print(*r)

