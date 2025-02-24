#pragma once
#include <math.h>
#include <deque>
#include <numeric>

/// \brief Infinite Impulse Response Filter
class LowPassFilter
{
public:
    LowPassFilter() = default;
    ~LowPassFilter() = default;

    LowPassFilter(float cutoff_frequnecy)
        : cutoff_frequnecy_(cutoff_frequnecy)
    {
    }

    float update(float new_value, float dt)
    {
        const auto alpha = std::exp(cutoff_frequnecy_ * dt);
        const auto new_value_ = alpha * new_value + (1.0f - alpha) * last_value_;
        last_value_ = new_value_;
        return new_value_;
    }

private:
    float cutoff_frequnecy_;
    float last_value_ = 0.0f;
};

/// \brief Moving Average Filter
class MovingAverageFilter
{
public:
    MovingAverageFilter() = default;
    ~MovingAverageFilter() = default;
    MovingAverageFilter(size_t num_samples)
        : max_samples_(num_samples)
    {
    }

    float update(float new_sample)
    {
        samples_.push_back(new_sample);
        if (samples_.size() > max_samples_)
        {
            samples_.pop_front();
            return std::accumulate(samples_.begin(), samples_.end(), 0.0) / max_samples_;
        }
        return std::accumulate(samples_.begin(), samples_.end(), 0.0) / samples_.size();
    }

private:
    size_t max_samples_;
    std::deque<float> samples_;
};