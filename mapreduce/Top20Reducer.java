import java.io.IOException;
import java.util.Map;
import java.util.HashMap;
import java.util.Comparator;
import java.util.PriorityQueue;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class Top20Reducer
        extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final Map<String, Integer> productTotals = new HashMap<>();

    @Override
    public void reduce(
            Text key,
            Iterable<IntWritable> values,
            Context context)
            throws IOException, InterruptedException {

        int total = 0;

        for (IntWritable value : values) {
            total += value.get();
        }

        productTotals.put(key.toString(), total);
    }

    @Override
    protected void cleanup(Context context)
            throws IOException, InterruptedException {

        PriorityQueue<Map.Entry<String, Integer>> top20 =
                new PriorityQueue<>(
                        20,
                        Comparator.comparingInt(Map.Entry::getValue)
                );

        for (Map.Entry<String, Integer> entry : productTotals.entrySet()) {

            top20.offer(entry);

            if (top20.size() > 20) {
                top20.poll();
            }
        }

        // Output highest-selling products first
        Map.Entry<String, Integer>[] result =
                new Map.Entry[top20.size()];

        int index = result.length - 1;

        while (!top20.isEmpty()) {
            result[index--] = top20.poll();
        }

        for (Map.Entry<String, Integer> entry : result) {
            context.write(
                    new Text(entry.getKey()),
                    new IntWritable(entry.getValue())
            );
        }
    }
}