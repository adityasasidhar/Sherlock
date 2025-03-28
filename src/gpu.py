import torch

def check_cuda_memory():
    if torch.cuda.is_available():
        total_memory = torch.cuda.get_device_properties(0).total_memory
        reserved_memory = torch.cuda.memory_reserved(0)
        allocated_memory = torch.cuda.memory_allocated(0)
        free_memory = reserved_memory - allocated_memory

        print(f"Total memory: {total_memory / (1024 ** 3):.2f} GB")
        print(f"Reserved memory: {reserved_memory / (1024 ** 3):.2f} GB")
        print(f"Allocated memory: {allocated_memory / (1024 ** 3):.2f} GB")
        print(f"Free memory: {free_memory / (1024 ** 3):.2f} GB")
    else:
        print("CUDA is not available. Running on CPU.")

def clear_cuda_memory():
    torch.cuda.empty_cache()
    print("CUDA memory is cleared.")

def get_cuda_device():
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0)
    else:
        return "CPU"

print(get_cuda_device())