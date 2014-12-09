#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include "MemoryManager.hpp"
#include "Signature.hpp"
#include "CallParser.hpp"

#include <vector>
#include <map>
#include <string>

class Sampler {
    private:
        std::map<std::string, Signature> signatures;

        MemoryManager mem;
        std::vector<CallParser> callparsers;

        std::vector<int> counters;

        template <typename T> void named_malloc(std::vector<std::string> &tokens, std::size_t multiplicity);
        void named_offset(std::vector<std::string> &tokens);
        void named_free(std::vector<std::string> &tokens);
        void add_call(std::vector<std::string> &tokens);
        void go();

    public:
        void set_counters(std::vector<std::string> &counters);
        void add_signature(Signature signature);
        void start();
};

#endif /* SAMPLER_HPP */
